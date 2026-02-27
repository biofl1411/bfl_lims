#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BFL LIMS - OCR 프록시 서버 (HTTPS)
Naver Clova OCR API를 브라우저에서 호출할 수 있도록 프록시 역할.
CORS 문제를 해결하고 Secret Key를 서버 측에 보관.
HTTPS 지원으로 GitHub Pages 등 HTTPS 페이지에서도 Mixed Content 없이 호출 가능.

실행: python ocr_proxy.py
포트: 5002 (HTTPS)

엔드포인트:
  POST /api/ocr/biz-license      — 사업자등록증 OCR (Document OCR)
  POST /api/ocr/general           — 인허가 문서 등 일반 OCR (General OCR)
  POST /api/ocr/inspection-form   — 시험·검사 의뢰서 OCR (Claude Vision)
  GET  /api/ocr/health            — 서버 상태 확인

SSL 인증서:
  ocr_proxy_cert.pem (자체서명 인증서)
  ocr_proxy_key.pem  (개인키)
  생성: openssl req -x509 -newkey rsa:2048 -keyout ocr_proxy_key.pem -out ocr_proxy_cert.pem -days 365 -nodes
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import time
import os
import ssl
import re
import anthropic

app = Flask(__name__)
CORS(app)

# ============================================================
# Naver Clova OCR 설정
# ============================================================
CLOVA_SECRET = os.environ.get(
    'CLOVA_OCR_SECRET',
    'QWpOSmx5d1NNb01abHhEQ1R3a01ZWUtMYXhxYVNXWnI='
)

CLOVA_BIZ_LICENSE_URL = os.environ.get(
    'CLOVA_BIZ_LICENSE_URL',
    'https://ialgkho4vv.apigw.ntruss.com/custom/v1/50335/'
    '4fd4f84e81ec1035e5c386fb4c1badc8eb704875c19495b491236d28fe232738'
    '/document/biz-license'
)

CLOVA_GENERAL_URL = os.environ.get(
    'CLOVA_GENERAL_URL',
    'https://ialgkho4vv.apigw.ntruss.com/custom/v1/50335/'
    '4fd4f84e81ec1035e5c386fb4c1badc8eb704875c19495b491236d28fe232738'
    '/general'
)

CLOVA_NAME_CARD_URL = os.environ.get(
    'CLOVA_NAME_CARD_URL',
    'https://ialgkho4vv.apigw.ntruss.com/custom/v1/50335/'
    '4fd4f84e81ec1035e5c386fb4c1badc8eb704875c19495b491236d28fe232738'
    '/document/name-card'
)

# ============================================================
# Claude Vision API 설정 (시험·검사 의뢰서 OCR)
# ============================================================
# 환경변수 우선, 없으면 ~/.claude_api_key 파일에서 읽기
CLAUDE_API_KEY = os.environ.get('CLAUDE_API_KEY', '')
if not CLAUDE_API_KEY:
    _key_file_path = os.path.expanduser('~/.claude_api_key')
    if os.path.exists(_key_file_path):
        with open(_key_file_path, 'r') as f:
            CLAUDE_API_KEY = f.read().strip()

INSPECTION_FORM_PROMPT = """이 이미지는 한국 식품 시험·검사 의뢰서입니다.
아래 JSON 형식으로 추출하세요. 값이 없으면 빈 문자열("").
배열이 비어있으면 빈 배열([]).
날짜는 YYYY-MM-DD 형식.

{
  "testPurpose": "검사목적 (자가품질위탁검사용/품질검사(의뢰)/수입식품검사/위생검사/유통식품검사/수거검사/재검사/이의신청검사/Allergen(RT-PCR)/잔류농약(참고용)/참고용(영양성분)/참고용(소비기한설정)/참고용(기준규격외)/연구용역/항생물질(참고용) 중 가장 가까운 것)",
  "testField": "시험분야 (식품/축산 중 하나. 의뢰서에 표시된 분야. 없으면 식품)",
  "companyName": "업체명 또는 영업소명",
  "representativeName": "대표자 또는 성명",
  "bizNo": "사업자등록번호 (000-00-00000 형식)",
  "licNo": "인허가번호 또는 허가번호",
  "phone": "전화번호",
  "fax": "팩스번호",
  "mobile": "휴대전화",
  "address": "소재지 또는 주소",
  "reportSend": ["성적서 수령방법 배열. 체크된 항목만. 우편/선발송/팩스(선)/메일(사본) 중"],
  "reportSendFax": "팩스 수령 번호 (있으면)",
  "reportSendEmail": "이메일 수령 주소 (있으면)",
  "samples": [
    {
      "productName": "제품명 또는 시료명",
      "foodType": "식품유형 또는 검체유형 (예: 과자, 빵류, 김치, 소스, 음료류, 기타가공품 등. 의뢰서에 기재된 품목유형/식품유형)",
      "inspectionItems": "검사항목 또는 시험항목 (예: 대장균군, 일반세균수, 납, 카드뮴 등. 쉼표 구분 문자열. 의뢰서에 기재된 검사할 항목들)",
      "manufactureNo": "제조번호 또는 LOT번호 또는 배치번호",
      "manufactureDate": "제조일자",
      "expiryDate": "유통기한 또는 소비기한 (날짜)",
      "expiryDays": "소비기한 일수 (제조일로부터 몇 일. 숫자만. 날짜가 아닌 일수로 기재된 경우)",
      "sampleAmount": "검체량 (숫자만)",
      "sampleAmountUnit": "검체량 단위 (g/kg/ml/L 중 하나)",
      "sampleCount": "검체수 (숫자)",
      "packageUnit": "포장단위",
      "transportStatus": "운반상태 (냉장/냉동/실온/상온 중 하나)"
    }
  ],
  "remarks": "비고 또는 특이사항"
}

JSON만 반환하세요. 설명이나 마크다운 없이 순수 JSON만."""


# ============================================================
# 헬스체크
# ============================================================
@app.route('/api/ocr/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'service': 'BFL OCR Proxy', 'port': 5002})


# ============================================================
# 사업자등록증 OCR (Document OCR — biz-license 특화 모델)
# ============================================================
@app.route('/api/ocr/biz-license', methods=['POST'])
def ocr_biz_license():
    """
    프론트에서 보내는 JSON 형식:
    {
      "version": "V2",
      "requestId": "...",
      "timestamp": 123456,
      "images": [{ "format": "jpg", "name": "file.jpg", "data": "<base64>" }]
    }
    """
    try:
        payload = request.get_json()
        if not payload:
            return jsonify({'error': 'JSON body required'}), 400

        headers = {
            'Content-Type': 'application/json',
            'X-OCR-SECRET': CLOVA_SECRET
        }

        resp = requests.post(
            CLOVA_BIZ_LICENSE_URL,
            headers=headers,
            json=payload,
            timeout=30
        )

        # Clova OCR 응답을 그대로 전달
        return jsonify(resp.json()), resp.status_code

    except requests.Timeout:
        return jsonify({'error': 'Clova OCR 타임아웃 (30초)'}), 504
    except requests.RequestException as e:
        return jsonify({'error': f'Clova OCR 요청 실패: {str(e)}'}), 502
    except Exception as e:
        return jsonify({'error': f'서버 오류: {str(e)}'}), 500


# ============================================================
# 명함 OCR (Document OCR — 명함 특화 모델)
# ============================================================
@app.route('/api/ocr/name-card', methods=['POST'])
def ocr_name_card():
    """
    명함 OCR: 이름, 회사, 부서, 전화번호, 이메일, 주소 등 추출
    """
    try:
        payload = request.get_json()
        if not payload:
            return jsonify({'error': 'JSON body required'}), 400

        headers = {
            'Content-Type': 'application/json',
            'X-OCR-SECRET': CLOVA_SECRET
        }

        resp = requests.post(
            CLOVA_NAME_CARD_URL,
            headers=headers,
            json=payload,
            timeout=30
        )

        return jsonify(resp.json()), resp.status_code

    except requests.Timeout:
        return jsonify({'error': 'Clova OCR 타임아웃 (30초)'}), 504
    except requests.RequestException as e:
        return jsonify({'error': f'Clova OCR 요청 실패: {str(e)}'}), 502
    except Exception as e:
        return jsonify({'error': f'서버 오류: {str(e)}'}), 500


# ============================================================
# 시험·검사 의뢰서 OCR (Claude Vision API)
# ============================================================
@app.route('/api/ocr/inspection-form', methods=['POST'])
def ocr_inspection_form():
    """
    시험·검사 의뢰서 이미지를 Claude Vision으로 분석하여 구조화된 JSON 반환.
    프론트에서 보내는 JSON:
    {
      "images": [{ "format": "jpg", "name": "file.jpg", "data": "<base64>" }]
    }
    """
    try:
        if not CLAUDE_API_KEY:
            return jsonify({'error': 'CLAUDE_API_KEY 환경변수가 설정되지 않았습니다'}), 500

        payload = request.get_json()
        if not payload or 'images' not in payload or not payload['images']:
            return jsonify({'error': 'images 배열이 필요합니다'}), 400

        image_info = payload['images'][0]
        image_base64 = image_info.get('data', '')
        image_format = image_info.get('format', 'jpeg').lower()

        if not image_base64:
            return jsonify({'error': '이미지 데이터(base64)가 비어있습니다'}), 400

        # 미디어 타입 결정
        if image_format in ('jpg', 'jpeg'):
            media_type = 'image/jpeg'
        elif image_format == 'png':
            media_type = 'image/png'
        elif image_format == 'webp':
            media_type = 'image/webp'
        elif image_format == 'gif':
            media_type = 'image/gif'
        else:
            media_type = 'image/jpeg'

        # Claude Vision API 호출
        client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
        message = client.messages.create(
            model='claude-haiku-4-5-20251001',
            max_tokens=2000,
            messages=[{
                'role': 'user',
                'content': [
                    {
                        'type': 'image',
                        'source': {
                            'type': 'base64',
                            'media_type': media_type,
                            'data': image_base64
                        }
                    },
                    {
                        'type': 'text',
                        'text': INSPECTION_FORM_PROMPT
                    }
                ]
            }]
        )

        # Claude 응답에서 JSON 추출
        result_text = message.content[0].text.strip()

        # 마크다운 코드블록 제거 (```json ... ```)
        if result_text.startswith('```'):
            result_text = re.sub(r'^```(?:json)?\s*', '', result_text)
            result_text = re.sub(r'\s*```$', '', result_text)

        result_json = json.loads(result_text)
        return jsonify(result_json)

    except json.JSONDecodeError as e:
        return jsonify({
            'error': f'Claude 응답 JSON 파싱 실패: {str(e)}',
            'raw': result_text[:500] if 'result_text' in dir() else ''
        }), 500
    except anthropic.APIError as e:
        return jsonify({'error': f'Claude API 오류: {str(e)}'}), 502
    except Exception as e:
        return jsonify({'error': f'서버 오류: {str(e)}'}), 500


# ============================================================
# 일반 OCR (General OCR — 인허가 문서 등)
# ============================================================
@app.route('/api/ocr/general', methods=['POST'])
def ocr_general():
    """
    General OCR: 모든 텍스트를 fields 배열로 반환
    """
    try:
        payload = request.get_json()
        if not payload:
            return jsonify({'error': 'JSON body required'}), 400

        headers = {
            'Content-Type': 'application/json',
            'X-OCR-SECRET': CLOVA_SECRET
        }

        resp = requests.post(
            CLOVA_GENERAL_URL,
            headers=headers,
            json=payload,
            timeout=30
        )

        return jsonify(resp.json()), resp.status_code

    except requests.Timeout:
        return jsonify({'error': 'Clova OCR 타임아웃 (30초)'}), 504
    except requests.RequestException as e:
        return jsonify({'error': f'Clova OCR 요청 실패: {str(e)}'}), 502
    except Exception as e:
        return jsonify({'error': f'서버 오류: {str(e)}'}), 500


# ============================================================
# 메인
# ============================================================
if __name__ == '__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    port = int(os.environ.get('OCR_PROXY_PORT', 5002))
    is_debug = os.environ.get('FLASK_DEBUG', '0') == '1'

    # SSL 인증서 경로 (스크립트와 같은 디렉터리)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    cert_file = os.path.join(base_dir, 'ocr_proxy_cert.pem')
    key_file = os.path.join(base_dir, 'ocr_proxy_key.pem')

    claude_status = '설정됨' if CLAUDE_API_KEY else '미설정 (CLAUDE_API_KEY 환경변수 필요)'

    if os.path.exists(cert_file) and os.path.exists(key_file):
        print(f'BFL OCR Proxy Server starting on port {port} (HTTPS)')
        print(f'  biz-license OCR:     POST https://localhost:{port}/api/ocr/biz-license')
        print(f'  name-card OCR:       POST https://localhost:{port}/api/ocr/name-card')
        print(f'  general OCR:         POST https://localhost:{port}/api/ocr/general')
        print(f'  inspection-form OCR: POST https://localhost:{port}/api/ocr/inspection-form')
        print(f'  health check:        GET  https://localhost:{port}/api/ocr/health')
        print(f'  SSL cert: {cert_file}')
        print(f'  Claude API Key: {claude_status}')
        app.run(host='0.0.0.0', port=port, debug=is_debug,
                use_reloader=False, ssl_context=(cert_file, key_file))
    else:
        print(f'[WARNING] SSL 인증서 없음 - HTTP 모드로 실행')
        print(f'  인증서 생성: openssl req -x509 -newkey rsa:2048 -keyout ocr_proxy_key.pem -out ocr_proxy_cert.pem -days 365 -nodes')
        print(f'BFL OCR Proxy Server starting on port {port} (HTTP)')
        print(f'  biz-license OCR:     POST http://localhost:{port}/api/ocr/biz-license')
        print(f'  name-card OCR:       POST http://localhost:{port}/api/ocr/name-card')
        print(f'  general OCR:         POST http://localhost:{port}/api/ocr/general')
        print(f'  inspection-form OCR: POST http://localhost:{port}/api/ocr/inspection-form')
        print(f'  health check:        GET  http://localhost:{port}/api/ocr/health')
        print(f'  Claude API Key: {claude_status}')
        app.run(host='0.0.0.0', port=port, debug=is_debug, use_reloader=False)

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

★ 양식 자동 판별 — 제목/헤더를 읽고 아래 8종 중 해당하는 양식을 판별하세요:
1. "식품유형" 헤더가 있으면 → formType="food" (식품 의뢰서, testField="식품", testPurpose="자가품질위탁검사용")
2. "축산물유형" 헤더가 있으면 → formType="livestock" (축산 의뢰서, testField="축산", testPurpose="자가품질위탁검사용")
3. "RT-PCR(Allergen)" 또는 "RT-PCR (Allergen)" 제목 → formType="allergen-pcr" (testField="식품", testPurpose="Allergen(RT-PCR)")
4. "Elisa" 제목 → formType="allergen-elisa" (testField="축산", testPurpose="Allergen(ELISA)")
5. "HPGe" 제목 → formType="radiation" (testField="식품", testPurpose="방사능(HPGe)")
6. "물질" 제목 → formType="material" (testField="식품", testPurpose="물질검사")
7. "RT-PCR" 제목 + "할랄" 또는 "Halal" 또는 "Vegan" → formType="halal-vegan" (testField="식품", testPurpose="Halal food(RT_PCR)" 또는 "Vegan food(RT-PCR)")
8. "소비기한" 제목 → formType="shelf-life" (testField="식품", testPurpose="참고용(소비기한설정)")

★ 격자(테이블) 인식 규칙:
- 표의 가로줄(행)과 세로줄(열)을 정확히 구분하세요.
- 각 셀의 값은 해당 열의 헤더에 정확히 매칭하세요.
- 병합된 셀(2행에 걸친 시료 정보)은 하나의 시료로 합치세요.
- 빈 행은 건너뛰세요. 데이터가 있는 행만 samples에 포함하세요.
- 손글씨는 글자 모양을 최대한 정확히 판독하세요. 불확실하면 가장 가까운 글자로.
- 체크표시(✓, V, ○, ●)는 해당 항목이 선택된 것입니다.
- 운반상태 체크란은 보통 오른쪽에 실온/상온/냉장/냉동 중 체크된 것을 읽으세요.

★ 양식별 시료 테이블 컬럼 차이:
- food/livestock: 순번, 제품명, 식품유형(축산물유형), 포장단위, 운반상태, 제조일자, 접수번호, 단서조항, 검체량, 소비기한
- allergen-pcr/allergen-elisa/halal-vegan: 순번, 접수번호, 샘플명, 유형(품번), 검사항목, 비고
- radiation: 순번, 접수번호, 샘플명, 유형(품번), 검사항목, 비고
- material: 순번, 접수번호, 분석장비, 시료상태, 실험방법, 샘플명칭
- shelf-life: 식품 의뢰서와 유사하되 소비기한 설정 관련 추가 필드

★ 텍스트 읽기 규칙:
- 한 글자씩 정확하게 읽으세요. 추측하지 마세요.
- 한글 제품명은 붙어있는 글자를 정확히 읽으세요.
- 날짜 "2026. 02. 10" 또는 "2026.02.10" → "2026-02-10"
- 성적서 발행 수량(국문/영문 부수)은 reportCopies에 기재하세요.

아래 JSON 형식으로 추출하세요. 값이 없으면 빈 문자열. 날짜는 YYYY-MM-DD.

{
  "formType": "food/livestock/allergen-pcr/allergen-elisa/radiation/material/halal-vegan/shelf-life",
  "testPurpose": "자동 판별된 검사목적",
  "testField": "식품 또는 축산",
  "companyName": "상호명",
  "representativeName": "대표자명",
  "bizNo": "사업자등록번호",
  "licNo": "인허가번호",
  "phone": "전화번호",
  "fax": "팩스번호",
  "mobile": "휴대전화",
  "address": "소재지",
  "reportSend": ["체크된 수령방법만 (우편/선발송/팩스/메일 중)"],
  "reportSendFax": "팩스번호",
  "reportSendEmail": "이메일",
  "reportCopies": {"korean": 0, "english": 0},
  "samples": [
    {
      "productName": "제품명/샘플명",
      "foodType": "식품유형/축산물유형/유형",
      "inspectionItems": "검사항목 (쉼표 구분)",
      "inspectionStandard": "단서조항/시험법",
      "manufactureNo": "제조번호/LOT",
      "manufactureDate": "YYYY-MM-DD",
      "expiryDate": "YYYY-MM-DD",
      "expiryDays": "소비기한 일수 (숫자만)",
      "sampleAmount": "검체량 (숫자만)",
      "sampleAmountUnit": "g/kg/ml/L",
      "sampleCount": "검체수 (기본 1)",
      "packageUnit": "포장단위",
      "transportStatus": "냉장/냉동/실온/상온",
      "analysisEquipment": "분석장비 (물질검사만: XRF/FTIR/현미경)",
      "sampleCondition": "시료상태 (물질검사만)",
      "experimentMethod": "실험방법 (물질검사만: 단일실험/비교실험)"
    }
  ],
  "billingInfo": {
    "billingDateType": "접수일/월말/특정날짜",
    "billingDate": "YYYY-MM-DD"
  },
  "remarks": "비고"
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
# 시험·검사 의뢰서 OCR (Clova OCR + Claude 구조화)
# 1단계: Naver Clova General OCR → 정확한 텍스트 추출
# 2단계: Claude → 추출 텍스트를 JSON 구조화
# ============================================================
@app.route('/api/ocr/inspection-form', methods=['POST'])
def ocr_inspection_form():
    """
    시험·검사 의뢰서 이미지를 Clova OCR로 텍스트 추출 후 Claude로 구조화.
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

        # ── 1단계: Clova General OCR로 텍스트 추출 ──
        clova_payload = {
            'version': 'V2',
            'requestId': f'insp-{int(time.time())}',
            'timestamp': int(time.time() * 1000),
            'images': [{
                'format': image_format if image_format in ('jpg', 'jpeg', 'png') else 'jpg',
                'name': image_info.get('name', 'file.jpg'),
                'data': image_base64
            }]
        }

        clova_headers = {
            'Content-Type': 'application/json',
            'X-OCR-SECRET': CLOVA_SECRET
        }

        clova_resp = requests.post(
            CLOVA_GENERAL_URL,
            headers=clova_headers,
            json=clova_payload,
            timeout=30
        )

        if clova_resp.status_code != 200:
            return jsonify({'error': f'Clova OCR 실패: {clova_resp.status_code}'}), 502

        clova_result = clova_resp.json()

        # Clova OCR 결과에서 텍스트 추출 (위치 정보 포함)
        extracted_lines = []
        if 'images' in clova_result:
            for img in clova_result['images']:
                for field in img.get('fields', []):
                    text = field.get('inferText', '').strip()
                    if text:
                        # 위치 정보 (y좌표 기준 행 그룹핑용)
                        vertices = field.get('boundingPoly', {}).get('vertices', [])
                        y = vertices[0].get('y', 0) if vertices else 0
                        x = vertices[0].get('x', 0) if vertices else 0
                        extracted_lines.append({
                            'text': text,
                            'x': x,
                            'y': y,
                            'lineBreak': field.get('lineBreak', False)
                        })

        # 행 단위로 그룹핑 (y좌표 차이 15px 이내면 같은 행)
        if extracted_lines:
            extracted_lines.sort(key=lambda f: (f['y'], f['x']))
            lines = []
            current_line = []
            last_y = -999
            for f in extracted_lines:
                if abs(f['y'] - last_y) > 15 and current_line:
                    lines.append(' '.join([w['text'] for w in current_line]))
                    current_line = []
                current_line.append(f)
                last_y = f['y']
                if f.get('lineBreak'):
                    lines.append(' '.join([w['text'] for w in current_line]))
                    current_line = []
                    last_y = -999
            if current_line:
                lines.append(' '.join([w['text'] for w in current_line]))
            ocr_text = '\n'.join(lines)
        else:
            ocr_text = ''

        if not ocr_text.strip():
            return jsonify({'error': 'OCR 텍스트 추출 실패 — 이미지를 확인하세요'}), 400

        # ── 2단계: Claude로 텍스트 구조화 ──
        client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
        message = client.messages.create(
            model='claude-sonnet-4-20250514',
            max_tokens=3000,
            messages=[{
                'role': 'user',
                'content': f"""아래는 한국 식품 시험·검사 의뢰서를 OCR로 읽은 텍스트입니다.

=== OCR 추출 텍스트 ===
{ocr_text}
=== 끝 ===

{INSPECTION_FORM_PROMPT}"""
            }]
        )

        # Claude 응답에서 JSON 추출
        result_text = message.content[0].text.strip()

        # 마크다운 코드블록 제거 (```json ... ```)
        if result_text.startswith('```'):
            result_text = re.sub(r'^```(?:json)?\s*', '', result_text)
            result_text = re.sub(r'\s*```$', '', result_text)

        result_json = json.loads(result_text)

        # OCR 원문 텍스트도 결과에 포함 (디버깅용)
        result_json['_ocrRawText'] = ocr_text[:2000]

        return jsonify(result_json)

    except json.JSONDecodeError as e:
        return jsonify({
            'error': f'Claude 응답 JSON 파싱 실패: {str(e)}',
            'raw': result_text[:500] if 'result_text' in locals() else ''
        }), 500
    except anthropic.APIError as e:
        return jsonify({'error': f'Claude API 오류: {str(e)}'}), 502
    except requests.Timeout:
        return jsonify({'error': 'Clova OCR 타임아웃 (30초)'}), 504
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

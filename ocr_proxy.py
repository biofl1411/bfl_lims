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

INSPECTION_FORM_PROMPT = """이 이미지는 (주)바이오푸드랩(BFL)의 시험·검사 의뢰서입니다.

★★★ 핵심 지시사항 ★★★
1. 이미지를 확대해서 한 글자씩 정밀하게 읽으세요.
2. 손글씨는 획의 모양을 분석하여 가장 가까운 한글/숫자로 판독하세요.
3. 인쇄된 텍스트와 손글씨를 구분하세요 — 인쇄된 것은 양식 레이블, 손글씨/타이핑된 것이 실제 데이터입니다.
4. 체크표시(✓, V, ○, ●, ■, 색칠된 박스)는 해당 항목이 선택된 것입니다.
5. 빈 칸은 빈 문자열("")로 반환하세요.

★ 양식 자동 판별 — 제목/헤더로 8종 판별:
1. 시료 테이블에 "식품유형" 헤더 → formType="food" (testField="식품", testPurpose="자가품질위탁검사용")
2. "축산물유형" 헤더 → formType="livestock" (testField="축산", testPurpose="자가품질위탁검사용")
3. "RT-PCR(Allergen)" 제목 → formType="allergen-pcr" (testField="식품", testPurpose="Allergen(RT-PCR)")
4. "Elisa" 제목 → formType="allergen-elisa" (testField="축산", testPurpose="Allergen(ELISA)")
5. "HPGe" 제목 → formType="radiation" (testField="식품", testPurpose="방사능(HPGe)")
6. "물질" 제목 → formType="material" (testField="식품", testPurpose="물질검사")
7. "RT-PCR" + "할랄/Halal/Vegan" → formType="halal-vegan"
8. "소비기한" 제목 → formType="shelf-life" (testPurpose="참고용(소비기한설정)")

★ 의뢰서 레이아웃 (위에서 아래 순서):
[상단] "시험·검사의뢰서" 제목 + BFL 로고
[의뢰인 정보]
  - "상 호" 오른쪽 → companyName (회사명. "(주)" 포함)
  - "대표자명" 오른쪽 → representativeName
  - "소 재 지" 오른쪽 → address (우편번호 포함)
  - "전 화" 오른쪽 → phone
  - "팩 스" 오른쪽 → fax
[업종] "업 종" 행 — 체크된 항목: 식품제조가공업/즉석판매제조가공업/유통판매업/식품소분업/기타
[검사목적] "검 사 목 적" 행 — 체크된 항목: 자가품질검사/자가품질검사(일부항목)/참고용/참고용(영양성분)
[성적서 구분] "성적서구분" — 국문 ( )부 / 영문 ( )부 — 괄호 안 숫자 읽기
[성적서수령방법] 체크된 항목: 우편/선발송/팩스선송부/메일선송부 + 이메일주소(@포함)
[성적서수령주소] 의뢰인소재지와동일 체크 또는 기타수령지 주소

[시료 테이블] — 행 수는 5~10행 가변. 데이터가 기입된 행만 추출:
  컬럼 헤더(2줄): 순번/접수번호 | 제품명 | 식품유형/단서조항 | 포장단위/검체량 | 운반상태 | 제조일자/소비기한(또는 품질유지기한) | 시험의뢰항목
  ※ "식품유형"과 "단서조항"은 같은 열의 위/아래 칸 (2행 병합)
  ※ "포장단위"와 "검체량"도 같은 열의 위/아래 칸
  ※ "제조일자"와 "소비기한"도 같은 열의 위/아래 칸
  ※ 운반상태는 드롭다운 또는 체크: 실온/상온/냉장/냉동

[하단]
  - 긴급협의일
  - 시료반환여부: 시료반환/시료폐기
  - 메모
  - 수수료(VAT포함): 금액
  - 납부구분: 카드/계좌이체(3일 이내 입금) 체크
  - 세금계산서: 발행/미발행/현금영수증 체크
  - 발행요청일, 입금예정일, 입금자명
  - 회사명/사업자번호, 계산서메일주소
  - 첨가물 제외 문구, 미생물 제외 문구
  - 개인정보 동의/비동의
  - 서명일자 (20__년 __월 __일)
  - 접수자, 의뢰인

★ 손글씨 판독 강화 규칙:
- 한글 자모 분리: ㄱㄴㄷㄹㅁㅂㅅㅇㅈㅊㅋㅌㅍㅎ + 모음 조합을 정확히
- 숫자: 0과 O, 1과 l, 6과 b, 8과 B 구분 주의
- 회사명에 자주 나오는 패턴: (주), 주식회사, 영농조합법인, 농업회사법인
- 전화번호: 0으로 시작, 지역번호-국번-번호 또는 010-XXXX-XXXX
- 날짜: 20XX. XX. XX 또는 20XX-XX-XX 또는 20XX년 XX월 XX일
- 금액: 숫자+쉼표 (예: 81,400)

★ 검사목적 판별 보강:
- "자가품질검사"에 체크 → testPurpose="자가품질위탁검사용"
- "참고용"에 체크 → testPurpose="참고용(기준규격외)"
- "참고용(영양성분)"에 체크 → testPurpose="참고용(영양성분)"
- 검사목적 체크란이 없거나 판독 불가 시 → testPurpose="" (빈 문자열)

아래 JSON 형식으로 추출. 값이 없으면 빈 문자열. 날짜는 YYYY-MM-DD.

{
  "formType": "food/livestock/allergen-pcr/allergen-elisa/radiation/material/halal-vegan/shelf-life",
  "testPurpose": "검사목적",
  "testField": "식품 또는 축산",
  "companyName": "상호 (회사명)",
  "representativeName": "대표자명",
  "bizNo": "사업자등록번호",
  "bizType": "체크된 업종 (식품제조가공업 등)",
  "licNo": "인허가번호",
  "phone": "전화번호",
  "fax": "팩스번호",
  "mobile": "휴대전화",
  "address": "소재지 (우편번호 포함)",
  "reportSend": ["체크된 수령방법 (우편/선발송/팩스/메일)"],
  "reportSendFax": "팩스 수령번호",
  "reportSendEmail": "이메일 수령주소 (@포함)",
  "reportCopies": {"korean": 1, "english": 0},
  "samples": [
    {
      "productName": "제품명 (손글씨 정밀 판독)",
      "foodType": "식품유형",
      "inspectionItems": "시험의뢰항목 (쉼표 구분)",
      "inspectionStandard": "단서조항",
      "manufactureNo": "제조번호/LOT",
      "manufactureDate": "YYYY-MM-DD",
      "expiryDate": "YYYY-MM-DD",
      "expiryDays": "소비기한 일수 (숫자만)",
      "sampleAmount": "검체량 (숫자만)",
      "sampleAmountUnit": "g/kg/ml/L",
      "sampleCount": "검체수 (기본 1)",
      "packageUnit": "포장단위 (예: 200g, 1ea, 500ml)",
      "transportStatus": "냉장/냉동/실온/상온"
    }
  ],
  "urgentDate": "긴급협의일 (YYYY-MM-DD)",
  "sampleReturn": "시료반환 또는 시료폐기",
  "memo": "메모 내용",
  "totalFee": "수수료 금액 (숫자만)",
  "paymentType": "납부구분 (카드/계좌이체)",
  "taxInvoice": "발행/미발행/현금영수증",
  "billingDate": "발행요청일 (YYYY-MM-DD)",
  "depositDate": "입금예정일 (YYYY-MM-DD)",
  "depositorName": "입금자명",
  "billingCompany": "회사명/사업자번호",
  "billingEmail": "계산서메일주소",
  "excludeAdditive": "첨가물 제외 관련 기재 내용",
  "excludeMicrobe": "미생물 제외 관련 기재 내용",
  "privacyConsent": "동의 또는 비동의",
  "signDate": "서명일자 (YYYY-MM-DD)",
  "receptionist": "접수자",
  "requester": "의뢰인",
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
# 시험·검사 의뢰서 OCR (Claude Vision API)
# ============================================================
@app.route('/api/ocr/inspection-form', methods=['POST'])
def ocr_inspection_form():
    """
    시험·검사 의뢰서 이미지를 Claude Vision으로 분석하여 구조화된 JSON 반환.
    """
    try:
        if not CLAUDE_API_KEY:
            return jsonify({'error': 'CLAUDE_API_KEY가 설정되지 않았습니다'}), 500

        payload = request.get_json()
        if not payload or 'images' not in payload or not payload['images']:
            return jsonify({'error': 'images 배열이 필요합니다'}), 400

        image_info = payload['images'][0]
        image_base64 = image_info.get('data', '')
        image_format = image_info.get('format', 'jpeg').lower()

        if not image_base64:
            return jsonify({'error': '이미지 데이터(base64)가 비어있습니다'}), 400

        # 미디어 타입 결정
        media_types = {'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png', 'webp': 'image/webp', 'gif': 'image/gif'}
        media_type = media_types.get(image_format, 'image/jpeg')

        # Claude Vision API 호출
        client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
        message = client.messages.create(
            model='claude-sonnet-4-20250514',
            max_tokens=4000,
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

        result_text = message.content[0].text.strip()

        # 마크다운 코드블록 제거
        if result_text.startswith('```'):
            result_text = re.sub(r'^```(?:json)?\s*', '', result_text)
            result_text = re.sub(r'\s*```$', '', result_text)

        result_json = json.loads(result_text)
        result_json['_ocrMethod'] = 'claude-vision'
        return jsonify(result_json)

    except json.JSONDecodeError as e:
        return jsonify({
            'error': f'Claude 응답 JSON 파싱 실패: {str(e)}',
            'raw': result_text[:500] if 'result_text' in locals() else ''
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

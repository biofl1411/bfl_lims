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
import base64
import io
import anthropic
import firebase_admin
from firebase_admin import credentials, firestore

try:
    from PIL import Image as PILImage
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    from pdf2image import convert_from_bytes
    HAS_PDF2IMAGE = True
except ImportError:
    HAS_PDF2IMAGE = False

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
    'https://oho2s9w1wf.apigw.ntruss.com/custom/v1/50990/'
    '999a55618e88f759fb3dbb8c622d327b86e210a65f6164bb2ce023e8186d48ce'
    '/general'
)
CLOVA_GENERAL_SECRET = os.environ.get(
    'CLOVA_GENERAL_SECRET',
    'TmhXWHFFcHB2ZnNlcFpZc2x1dHZuYmxQSndqenlubk8='
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

# ============================================================
# Firebase Admin 초기화 (OCR 보정 사전용)
# ============================================================
_firebase_db = None
try:
    _sa_key_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'serviceAccountKey.json')
    if not os.path.exists(_sa_key_path):
        _sa_key_path = '/home/biofl/bfl_lims/serviceAccountKey.json'
    if os.path.exists(_sa_key_path):
        if not firebase_admin._apps:
            _cred = credentials.Certificate(_sa_key_path)
            firebase_admin.initialize_app(_cred)
        _firebase_db = firestore.client()
        print(f'[OCR] Firebase Admin 초기화 완료 (보정 사전 사용 가능)')
    else:
        print(f'[OCR] serviceAccountKey.json 없음 — 보정 사전 비활성')
except Exception as _fb_err:
    print(f'[OCR] Firebase Admin 초기화 실패: {_fb_err} — 보정 사전 비활성')


# ============================================================
# 한글 초성/중성/종성 분해 (보정 패턴 분석용)
# ============================================================
_CHO = ['ㄱ','ㄲ','ㄴ','ㄷ','ㄸ','ㄹ','ㅁ','ㅂ','ㅃ','ㅅ','ㅆ','ㅇ','ㅈ','ㅉ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ']
_JUNG = ['ㅏ','ㅐ','ㅑ','ㅒ','ㅓ','ㅔ','ㅕ','ㅖ','ㅗ','ㅘ','ㅙ','ㅚ','ㅛ','ㅜ','ㅝ','ㅞ','ㅟ','ㅠ','ㅡ','ㅢ','ㅣ']

def decompose_hangul(ch):
    """한글 한 글자를 초성/중성/종성으로 분해"""
    code = ord(ch)
    if code < 0xAC00 or code > 0xD7A3:
        return None
    offset = code - 0xAC00
    cho_idx = offset // (21 * 28)
    jung_idx = (offset % (21 * 28)) // 28
    return {'cho': _CHO[cho_idx], 'jung': _JUNG[jung_idx]}


def load_ocr_corrections(requester=None, limit=50):
    """Firestore에서 OCR 보정 이력 로드 → 손글씨 오인식 패턴 문자열 생성"""
    if not _firebase_db:
        return ''
    try:
        query = _firebase_db.collection('ocrCorrections').order_by(
            'timestamp', direction=firestore.Query.DESCENDING
        ).limit(limit)
        if requester:
            query = _firebase_db.collection('ocrCorrections').where(
                'requester', '==', requester
            ).order_by('timestamp', direction=firestore.Query.DESCENDING).limit(limit)

        docs = query.stream()
        # 패턴 집계: (ocr글자 → fix글자) 빈도
        patterns = {}
        for doc in docs:
            data = doc.to_dict()
            for corr in data.get('corrections', []):
                for cd in corr.get('charDiff', []):
                    ocr_ch = cd.get('ocr', '')
                    fix_ch = cd.get('fix', '')
                    if ocr_ch and fix_ch and ocr_ch != fix_ch:
                        key = f'{ocr_ch}→{fix_ch}'
                        patterns[key] = patterns.get(key, 0) + 1

        if not patterns:
            return ''

        # 빈도순 정렬
        sorted_patterns = sorted(patterns.items(), key=lambda x: -x[1])
        pattern_strs = [f'{k} ({v}회)' for k, v in sorted_patterns[:20]]

        prefix = ''
        if requester:
            prefix = f'이 의뢰서 작성자({requester})의 '
        return f'\n\n★ OCR 보정 사전 — {prefix}손글씨 오인식 패턴:\n' + ', '.join(pattern_strs) + '\n위 패턴을 참고하여 손글씨 판독 시 보정하세요.'
    except Exception as e:
        print(f'[OCR] 보정 사전 로드 실패: {e}')
        return ''


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
- 단위 "g"와 숫자 "9" 혼동 주의: 손글씨 "g"는 "9"처럼 보일 수 있음 → 포장단위/검체량 뒤의 숫자가 맥락상 단위(g,kg,ml,L)인지 확인. 예: "400g"이 "4009"로 보이면 "400g"이 맞음
- 수량 "개": "2개", "14개" 등 수량 뒤에 "개"가 붙을 수 있음 → 숫자만 추출. 예: "X 2개" → sampleCount=2
- 포장단위/검체량: "200g x 14" → packageUnit="200g", sampleAmount="200", sampleCount="14" (곱하지 말 것)
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
# 시험·검사 의뢰서 OCR (Clova General OCR → Claude 구조화)
# 1단계: Clova General OCR로 정확한 텍스트 추출
# 2단계: Claude로 추출 텍스트를 JSON 구조화
# ============================================================
@app.route('/api/ocr/inspection-form', methods=['POST'])
def ocr_inspection_form():
    """
    시험·검사 의뢰서: Clova General OCR 텍스트 추출 + Claude JSON 구조화.
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

        # PDF → 이미지 변환 (Claude API는 PDF를 직접 받지 못함)
        claude_image_base64 = image_base64
        claude_media_type = None
        if image_format == 'pdf':
            if not HAS_PDF2IMAGE:
                return jsonify({'error': 'PDF 변환 라이브러리(pdf2image)가 설치되지 않았습니다'}), 500
            pdf_bytes = base64.b64decode(image_base64)
            pages = convert_from_bytes(pdf_bytes, dpi=200, first_page=1, last_page=1)
            if pages:
                buf = io.BytesIO()
                pages[0].save(buf, format='JPEG', quality=92)
                claude_image_base64 = base64.b64encode(buf.getvalue()).decode()
                claude_media_type = 'image/jpeg'
                app.logger.info(f'[OCR] PDF → JPEG 변환 완료 ({len(claude_image_base64)//1024}KB)')

        # ── 1단계: Clova General OCR ──
        clova_payload = {
            'version': 'V2',
            'requestId': f'insp-{int(time.time())}',
            'timestamp': int(time.time() * 1000),
            'lang': 'ko',
            'images': [{
                'format': image_format if image_format in ('jpg', 'jpeg', 'png', 'pdf', 'tiff') else 'jpg',
                'name': image_info.get('name', 'file.jpg'),
                'data': image_base64
            }]
        }

        clova_resp = requests.post(
            CLOVA_GENERAL_URL,
            headers={'Content-Type': 'application/json', 'X-OCR-SECRET': CLOVA_GENERAL_SECRET},
            json=clova_payload,
            timeout=30
        )

        if clova_resp.status_code != 200:
            return jsonify({'error': f'Clova OCR 실패: {clova_resp.status_code} - {clova_resp.text[:200]}'}), 502

        clova_result = clova_resp.json()

        # 텍스트 추출 (행 단위 그룹핑)
        extracted = []
        if 'images' in clova_result:
            for img in clova_result['images']:
                for field in img.get('fields', []):
                    text = field.get('inferText', '').strip()
                    if text:
                        vertices = field.get('boundingPoly', {}).get('vertices', [])
                        y = vertices[0].get('y', 0) if vertices else 0
                        x = vertices[0].get('x', 0) if vertices else 0
                        extracted.append({'text': text, 'x': x, 'y': y, 'lb': field.get('lineBreak', False)})

        if not extracted:
            return jsonify({'error': 'OCR 텍스트 추출 실패 — 이미지를 확인하세요'}), 400

        # 행 단위 그룹핑 (y좌표 차이 12px 이내 = 같은 행)
        extracted.sort(key=lambda f: (f['y'], f['x']))
        lines = []
        cur = []
        last_y = -999
        for f in extracted:
            if abs(f['y'] - last_y) > 12 and cur:
                lines.append(' '.join([w['text'] for w in cur]))
                cur = []
            cur.append(f)
            last_y = f['y']
            if f.get('lb'):
                lines.append(' '.join([w['text'] for w in cur]))
                cur = []
                last_y = -999
        if cur:
            lines.append(' '.join([w['text'] for w in cur]))

        ocr_text = '\n'.join(lines)

        # ── 2단계: Claude 구조화 (텍스트 + 이미지 동시 전달) ──
        if not claude_media_type:
            media_types = {'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png', 'webp': 'image/webp', 'gif': 'image/gif'}
            claude_media_type = media_types.get(image_format, 'image/jpeg')

        # OCR 보정 사전 로드 (requester 파라미터가 있으면 해당 담당자 패턴만)
        requester = payload.get('requester', '')
        correction_hint = load_ocr_corrections(requester if requester else None)

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
                            'media_type': claude_media_type,
                            'data': claude_image_base64
                        }
                    },
                    {
                        'type': 'text',
                        'text': f"""위 이미지는 (주)바이오푸드랩(BFL)의 시험·검사 의뢰서입니다.
아래는 Clova OCR로 추출한 텍스트입니다. OCR 텍스트를 기본으로 사용하되,
텍스트에서 누락되거나 불확실한 부분은 이미지를 직접 확인하여 보완하세요.

=== Clova OCR 텍스트 ===
{ocr_text}
=== 끝 ===

{INSPECTION_FORM_PROMPT}{correction_hint}"""
                    }
                ]
            }]
        )

        result_text = message.content[0].text.strip()
        if result_text.startswith('```'):
            result_text = re.sub(r'^```(?:json)?\s*', '', result_text)
            result_text = re.sub(r'\s*```$', '', result_text)

        result_json = json.loads(result_text)
        result_json['_ocrMethod'] = 'clova-general+claude'
        result_json['_ocrRawText'] = ocr_text[:3000]
        return jsonify(result_json)

    except json.JSONDecodeError as e:
        return jsonify({
            'error': f'Claude 응답 JSON 파싱 실패: {str(e)}',
            'raw': result_text[:500] if 'result_text' in locals() else ''
        }), 500
    except anthropic.APIError as e:
        return jsonify({'error': f'Claude API 오류: {str(e)}'}), 502
    except requests.Timeout:
        return jsonify({'error': 'Clova OCR 타임아웃'}), 504
    except Exception as e:
        return jsonify({'error': f'서버 오류: {str(e)}'}), 500


# ============================================================
# 템플릿 기반 특화 OCR (좌표 크롭 → Clova OCR → 직접 매핑)
# ============================================================
@app.route('/api/ocr/template-ocr', methods=['POST'])
def ocr_template():
    """
    템플릿 기반 의뢰서 OCR:
    1. Firestore에서 해당 양식의 활성 템플릿 로드
    2. 이미지를 필드별 좌표로 크롭
    3. 각 크롭 이미지를 Clova OCR에 개별 전송
    4. 결과를 직접 필드에 매핑
    5. 확신도 낮은 필드만 Claude에 보정 요청

    요청 JSON:
    {
      "images": [{ "format": "jpg", "name": "file.jpg", "data": "<base64>" }],
      "formType": "food" (선택 — 없으면 자동 판별),
      "requester": "담당자명" (선택)
    }
    """
    try:
        payload = request.get_json()
        if not payload or 'images' not in payload or not payload['images']:
            return jsonify({'error': 'images 배열이 필요합니다'}), 400

        image_info = payload['images'][0]
        image_base64 = image_info.get('data', '')
        image_format = image_info.get('format', 'jpeg').lower()

        if not image_base64:
            return jsonify({'error': '이미지 데이터(base64)가 비어있습니다'}), 400

        # ── 1. Firestore에서 템플릿 로드 ──
        form_type = payload.get('formType', '')
        template = _load_ocr_template(form_type)

        if not template:
            return _fallback_to_claude_ocr(payload)

        regions = template.get('regions', {})
        if not regions:
            return _fallback_to_claude_ocr(payload)

        print(f'[OCR] 템플릿 로드 성공: {template.get("_id")} (필드 {len(regions)}개)')

        # ── 2. Clova로 전체 이미지 OCR (기존과 동일) ──
        clova_payload = {
            'version': 'V2',
            'requestId': f'tpl-{int(time.time() * 1000)}',
            'timestamp': int(time.time() * 1000),
            'lang': 'ko',
            'images': [{
                'format': image_format if image_format in ('jpg', 'jpeg', 'png') else 'jpg',
                'name': image_info.get('name', 'image.jpg'),
                'data': image_base64
            }]
        }
        clova_resp = requests.post(
            CLOVA_GENERAL_URL,
            headers={'Content-Type': 'application/json', 'X-OCR-SECRET': CLOVA_GENERAL_SECRET},
            json=clova_payload,
            timeout=30
        )

        ocr_text = ''
        if clova_resp.status_code == 200:
            clova_result = clova_resp.json()
            extracted = []
            if 'images' in clova_result:
                for img in clova_result['images']:
                    for field in img.get('fields', []):
                        text = field.get('inferText', '').strip()
                        if text:
                            vertices = field.get('boundingPoly', {}).get('vertices', [])
                            y = vertices[0].get('y', 0) if vertices else 0
                            x = vertices[0].get('x', 0) if vertices else 0
                            extracted.append({'text': text, 'x': x, 'y': y, 'lb': field.get('lineBreak', False)})

            if extracted:
                extracted.sort(key=lambda f: (f['y'], f['x']))
                lines = []
                cur = []
                last_y = -999
                for f in extracted:
                    if abs(f['y'] - last_y) > 12 and cur:
                        lines.append(' '.join([w['text'] for w in cur]))
                        cur = []
                    cur.append(f)
                    last_y = f['y']
                    if f.get('lb'):
                        lines.append(' '.join([w['text'] for w in cur]))
                        cur = []
                        last_y = -999
                if cur:
                    lines.append(' '.join([w['text'] for w in cur]))
                ocr_text = '\n'.join(lines)

        print(f'[OCR] Clova 전체 OCR 완료 ({len(ocr_text)}자)')

        # ── 3. 체크박스 필드 크롭 (PIL 사용) ──
        checkbox_crops_b64 = {}
        CHECKBOX_FIELDS = {'bizType', 'testPurpose', 'reportSend', 'reportAddress',
                           'reportCopies', 'sampleReturn', 'taxInvoice', 'paymentType'}

        if HAS_PIL:
            img_bytes = base64.b64decode(image_base64)
            pil_img = PILImage.open(io.BytesIO(img_bytes))
            img_w, img_h = pil_img.size

            for field_key in CHECKBOX_FIELDS:
                region = regions.get(field_key)
                if not region:
                    continue
                crop_x = max(0, int(region['x'] * img_w))
                crop_y = max(0, int(region['y'] * img_h))
                crop_r = min(img_w, crop_x + int(region['w'] * img_w))
                crop_b = min(img_h, crop_y + int(region['h'] * img_h))
                if crop_r <= crop_x or crop_b <= crop_y:
                    continue
                cropped = pil_img.crop((crop_x, crop_y, crop_r, crop_b))
                buf = io.BytesIO()
                cropped.save(buf, format='JPEG', quality=95)
                checkbox_crops_b64[field_key] = base64.b64encode(buf.getvalue()).decode('utf-8')

        # ── 4. Claude에 전체 이미지 + Clova 텍스트 + 좌표 힌트 전달 ──
        media_types = {'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png', 'webp': 'image/webp'}
        media_type = media_types.get(image_format, 'image/jpeg')

        requester = payload.get('requester', '')
        correction_hint = load_ocr_corrections(requester if requester else None)

        # 좌표 힌트 생성 — 템플릿 좌표를 Claude에 알려줌
        coord_hints = []
        for field_key, region in regions.items():
            if field_key not in CHECKBOX_FIELDS:
                pct_x = int(region['x'] * 100)
                pct_y = int(region['y'] * 100)
                pct_w = int(region['w'] * 100)
                pct_h = int(region['h'] * 100)
                coord_hints.append(f'  - {field_key}: 위치({pct_x}%,{pct_y}%) 크기({pct_w}%x{pct_h}%)')
        coord_hint_text = '\n'.join(coord_hints)

        # Claude 메시지 구성 — 전체 이미지 + 체크박스 크롭 이미지들
        claude_content = [
            {
                'type': 'image',
                'source': {'type': 'base64', 'media_type': media_type, 'data': image_base64}
            }
        ]

        # 체크박스 크롭 이미지도 추가
        checkbox_image_desc = []
        for idx, (ck_key, ck_b64) in enumerate(checkbox_crops_b64.items()):
            claude_content.append({
                'type': 'image',
                'source': {'type': 'base64', 'media_type': 'image/jpeg', 'data': ck_b64}
            })
            checkbox_image_desc.append(f'  이미지{idx+2}: {ck_key} 체크박스 영역 크롭')

        checkbox_desc = '\n'.join(checkbox_image_desc) if checkbox_image_desc else ''

        claude_content.append({
            'type': 'text',
            'text': f"""위 이미지는 (주)바이오푸드랩(BFL)의 시험·검사 의뢰서입니다.
이미지1: 전체 의뢰서 원본
{checkbox_desc}

아래는 Clova OCR로 추출한 텍스트입니다. OCR 텍스트를 기본으로 사용하되,
텍스트에서 누락되거나 불확실한 부분은 이미지를 직접 확인하여 보완하세요.

=== Clova OCR 텍스트 ===
{ocr_text}
=== 끝 ===

★ 템플릿 좌표 힌트 (각 필드가 이미지의 어느 위치에 있는지):
{coord_hint_text}

★ 체크박스 필드는 크롭 이미지를 직접 보고 체크 상태를 판독하세요:
  - bizType: 체크된 업종 (식품제조가공업/즉석판매제조가공업/유통판매업/식품소분업/기타)
  - testPurpose: 체크된 검사목적 (자가품질검사/자가품질검사(일부항목)/참고용/참고용(영양성분))
  - reportSend: 체크된 수령방법 배열 (우편/선발송/팩스선송부/메일선송부)
  - reportCopies: 국문/영문 부수 {{"korean": 숫자, "english": 숫자}}
  - sampleReturn: 시료반환 또는 시료폐기
  - taxInvoice: 발행/미발행/현금영수증
  - paymentType: 카드/계좌이체

{INSPECTION_FORM_PROMPT}{correction_hint}"""
        })

        client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
        message = client.messages.create(
            model='claude-sonnet-4-20250514',
            max_tokens=4000,
            messages=[{'role': 'user', 'content': claude_content}]
        )

        result_text = message.content[0].text.strip()
        if result_text.startswith('```'):
            result_text = re.sub(r'^```(?:json)?\s*', '', result_text)
            result_text = re.sub(r'\s*```$', '', result_text)

        result_json = json.loads(result_text)

        # 메모란에서 팩스/이메일 자동 추출
        _extract_contact_from_memo(result_json)

        # 메타정보 추가
        result_json['formType'] = result_json.get('formType', template.get('formType', form_type))
        result_json['_ocrMethod'] = 'template-crop+clova'
        result_json['_templateId'] = template.get('_id', '')
        result_json['_mappedFields'] = len(regions)
        result_json['_ocrRawText'] = ocr_text[:3000]

        print(f'[OCR] 템플릿+Claude 하이브리드 OCR 완료')
        return jsonify(result_json)

    except json.JSONDecodeError as je:
        print(f'[OCR] 템플릿 OCR Claude JSON 파싱 실패: {je}')
        try:
            return _fallback_to_claude_ocr(payload)
        except:
            return jsonify({'error': f'JSON 파싱 실패: {str(je)}'}), 500
    except Exception as e:
        print(f'[OCR] 템플릿 OCR 오류: {e}')
        import traceback
        traceback.print_exc()
        # 오류 시 기존 방식 폴백
        try:
            return _fallback_to_claude_ocr(payload)
        except Exception:
            return jsonify({'error': f'서버 오류: {str(e)}'}), 500


def _claude_read_checkboxes(checkbox_crops):
    """체크박스 크롭 이미지들을 Claude Vision으로 일괄 판독"""
    if not CLAUDE_API_KEY or not checkbox_crops:
        return {}

    try:
        # 모든 체크박스 크롭을 하나의 요청으로 전송
        content_blocks = []
        field_list = []

        for field_key, crop_b64 in checkbox_crops.items():
            content_blocks.append({
                'type': 'image',
                'source': {'type': 'base64', 'media_type': 'image/jpeg', 'data': crop_b64}
            })
            content_blocks.append({
                'type': 'text',
                'text': f'↑ 위 이미지는 "{field_key}" 필드입니다.'
            })
            field_list.append(field_key)

        field_instructions = {
            'bizType': '업종 — 체크된 항목 반환 (식품제조가공업/즉석판매제조가공업/유통판매업/식품소분업/기타)',
            'testPurpose': '검사목적 — 체크된 항목 반환 (자가품질검사/자가품질검사(일부항목)/참고용/참고용(영양성분))',
            'reportSend': '성적서수령방법 — 체크된 항목을 배열로 반환 (우편/선발송/팩스선송부/메일선송부)',
            'reportAddress': '수령주소 — 체크된 항목 반환 (의뢰인소재지와동일/기타수령지) + 기타 시 괄호 안 주소',
            'reportCopies': '성적서 부수 — {"korean": 숫자, "english": 숫자} 형식',
            'sampleReturn': '시료반환여부 — 체크된 항목 반환 (시료반환/시료폐기)',
            'taxInvoice': '세금계산서 — 체크된 항목 반환 (발행/미발행/현금영수증)',
            'paymentType': '납부구분 — 체크된 항목 반환 (현금/카드/계좌이체)'
        }

        instructions = '\n'.join([f'- {k}: {field_instructions.get(k, "체크된 항목 반환")}' for k in field_list])

        content_blocks.append({
            'type': 'text',
            'text': f"""위 이미지들은 의뢰서의 체크박스 영역입니다.
각 이미지에서 체크(✓, V, ○, ●, ■, 색칠된 박스)된 항목을 읽어주세요.

필드별 반환 형식:
{instructions}

JSON 객체로 반환하세요. 체크가 없으면 빈 문자열.
reportSend는 배열, reportCopies는 객체, 나머지는 문자열.
JSON만 반환하세요."""
        })

        client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
        message = client.messages.create(
            model='claude-sonnet-4-20250514',
            max_tokens=1000,
            messages=[{'role': 'user', 'content': content_blocks}]
        )

        text = message.content[0].text.strip()
        if text.startswith('```'):
            text = re.sub(r'^```(?:json)?\s*', '', text)
            text = re.sub(r'\s*```$', '', text)
        return json.loads(text)
    except Exception as e:
        print(f'[OCR] 체크박스 Claude 판독 실패: {e}')
        return {}


def _extract_contact_from_memo(result):
    """메모란 텍스트에서 팩스번호/이메일 패턴을 추출하여 해당 필드에 보충"""
    memo = result.get('memo', '')
    if not memo:
        return

    # 이메일 패턴 추출 (여러 개 가능)
    emails = re.findall(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}', memo)
    if emails:
        existing_email = result.get('reportSendEmail', '').strip()
        if not existing_email:
            result['reportSendEmail'] = emails[0]
        # 추가 이메일이 있으면 billingEmail에도
        if len(emails) > 1 and not result.get('billingEmail', '').strip():
            result['billingEmail'] = emails[1]
        elif len(emails) == 1 and not result.get('billingEmail', '').strip():
            result['billingEmail'] = emails[0]

    # 팩스번호 패턴 추출 (0으로 시작하는 전화번호 형태 + 팩스/fax/FAX 키워드 근처)
    fax_patterns = re.findall(r'(?:팩스|fax|FAX|Fax)\s*[:\.]?\s*(0\d{1,2}[\-.\s]?\d{3,4}[\-.\s]?\d{4})', memo, re.IGNORECASE)
    if fax_patterns:
        existing_fax = result.get('reportSendFax', '').strip()
        if not existing_fax:
            result['reportSendFax'] = fax_patterns[0].strip()

    # 메모에서 추출된 연락처 정보를 메모 원문에서 제거하지 않음 (원문 보존)


def _load_ocr_template(form_type=''):
    """Firestore에서 활성 OCR 템플릿 로드"""
    if not _firebase_db:
        return None
    try:
        if form_type:
            docs = _firebase_db.collection('ocrTemplates').where(
                'formType', '==', form_type
            ).where('active', '==', True).limit(1).stream()
        else:
            # formType 미지정 시 food 기본
            docs = _firebase_db.collection('ocrTemplates').where(
                'active', '==', True
            ).limit(1).stream()

        for doc in docs:
            data = doc.to_dict()
            data['_id'] = doc.id
            return data
        return None
    except Exception as e:
        print(f'[OCR] 템플릿 로드 실패: {e}')
        return None


def _clova_ocr_single(crop_base64, fmt='jpeg'):
    """단일 크롭 이미지에 대해 Clova General OCR 호출 → 텍스트 반환"""
    try:
        clova_payload = {
            'version': 'V2',
            'requestId': f'crop-{int(time.time() * 1000)}',
            'timestamp': int(time.time() * 1000),
            'lang': 'ko',
            'images': [{
                'format': fmt if fmt in ('jpg', 'jpeg', 'png') else 'jpg',
                'name': 'crop.jpg',
                'data': crop_base64
            }]
        }

        resp = requests.post(
            CLOVA_GENERAL_URL,
            headers={'Content-Type': 'application/json', 'X-OCR-SECRET': CLOVA_GENERAL_SECRET},
            json=clova_payload,
            timeout=15
        )

        if resp.status_code != 200:
            return ''

        result = resp.json()
        texts = []
        if 'images' in result:
            for img in result['images']:
                for field in img.get('fields', []):
                    t = field.get('inferText', '').strip()
                    if t:
                        texts.append(t)
        return ' '.join(texts)
    except Exception as e:
        print(f'[OCR] Clova 크롭 OCR 실패: {e}')
        return ''


def _parse_sample_table_with_claude(sample_fields, image_base64, image_format, regions, img_w, img_h, requester=''):
    """시료 테이블 영역을 Claude로 구조화"""
    if not CLAUDE_API_KEY:
        return []

    try:
        # 시료 테이블 영역 크롭
        region = regions.get('sampleTable')
        if not region:
            return []

        img_bytes = base64.b64decode(image_base64)
        pil_img = PILImage.open(io.BytesIO(img_bytes))

        crop_x = int(region['x'] * img_w)
        crop_y = int(region['y'] * img_h)
        crop_r = min(img_w, crop_x + int(region['w'] * img_w))
        crop_b = min(img_h, crop_y + int(region['h'] * img_h))
        cropped = pil_img.crop((crop_x, crop_y, crop_r, crop_b))

        buf = io.BytesIO()
        cropped.save(buf, format='JPEG', quality=95)
        table_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')

        # OCR 텍스트도 전달
        table_text = sample_fields.get('sampleTable', '')

        correction_hint = load_ocr_corrections(requester if requester else None)

        client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
        message = client.messages.create(
            model='claude-sonnet-4-20250514',
            max_tokens=2000,
            messages=[{
                'role': 'user',
                'content': [
                    {
                        'type': 'image',
                        'source': {'type': 'base64', 'media_type': 'image/jpeg', 'data': table_b64}
                    },
                    {
                        'type': 'text',
                        'text': f"""이 이미지는 시험·검사 의뢰서의 시료 테이블 부분입니다.

OCR 텍스트: {table_text}

데이터가 기입된 행만 JSON 배열로 추출하세요. 빈 행은 무시.
각 행의 형식:
{{"productName":"제품명","foodType":"식품유형","inspectionItems":"시험항목(쉼표구분)","inspectionStandard":"단서조항","manufactureNo":"제조번호","manufactureDate":"YYYY-MM-DD","expiryDate":"YYYY-MM-DD","expiryDays":"일수","sampleAmount":"숫자","sampleAmountUnit":"g/kg/ml/L","sampleCount":"1","packageUnit":"포장단위","transportStatus":"냉장/냉동/실온/상온"}}

손글씨를 정밀하게 판독하세요. 날짜는 YYYY-MM-DD 형식.{correction_hint}

JSON 배열만 반환하세요."""
                    }
                ]
            }]
        )

        text = message.content[0].text.strip()
        if text.startswith('```'):
            text = re.sub(r'^```(?:json)?\s*', '', text)
            text = re.sub(r'\s*```$', '', text)
        return json.loads(text)
    except Exception as e:
        print(f'[OCR] 시료 테이블 Claude 파싱 실패: {e}')
        return []


def _assemble_sample_rows(sample_fields):
    """개별 열 OCR 결과를 행 단위로 조합"""
    # 각 열의 텍스트를 줄바꿈으로 분리하여 행 매칭
    col_map = {
        'sample_productName': 'productName',
        'sample_foodType': 'foodType',
        'sample_inspItems': 'inspectionItems',
        'sample_standard': 'inspectionStandard',
        'sample_pkgUnit': 'packageUnit',
        'sample_amount': 'sampleAmount',
        'sample_transport': 'transportStatus',
        'sample_mfgDate': 'manufactureDate',
        'sample_expDate': 'expiryDate'
    }

    # 각 열을 줄 단위로 분리
    col_lines = {}
    max_rows = 0
    for src_key, dest_key in col_map.items():
        text = sample_fields.get(src_key, '')
        lines = [l.strip() for l in text.split('\n') if l.strip()] if text else []
        col_lines[dest_key] = lines
        max_rows = max(max_rows, len(lines))

    if max_rows == 0:
        return []

    samples = []
    for i in range(max_rows):
        row = {}
        for dest_key, lines in col_lines.items():
            row[dest_key] = lines[i] if i < len(lines) else ''
        # 최소 제품명이 있는 행만 포함
        if row.get('productName', '').strip():
            samples.append(row)

    return samples


def _claude_correct_fields(uncertain_fields, image_base64, image_format, regions, img_w, img_h, requester=''):
    """불확실한 필드를 Claude로 보정"""
    if not CLAUDE_API_KEY or not uncertain_fields:
        return {}

    try:
        # 불확실한 필드 영역만 크롭하여 하나의 이미지로 전달
        media_types = {'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png'}
        media_type = media_types.get(image_format, 'image/jpeg')

        field_descriptions = []
        for key in uncertain_fields:
            region = regions.get(key)
            if region:
                field_descriptions.append(f'- {key}: 이미지 좌표 ({int(region["x"]*100)}%, {int(region["y"]*100)}%) 크기 ({int(region["w"]*100)}%x{int(region["h"]*100)}%)')

        if not field_descriptions:
            return {}

        correction_hint = load_ocr_corrections(requester if requester else None)

        client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
        message = client.messages.create(
            model='claude-sonnet-4-20250514',
            max_tokens=1000,
            messages=[{
                'role': 'user',
                'content': [
                    {
                        'type': 'image',
                        'source': {'type': 'base64', 'media_type': media_type, 'data': image_base64}
                    },
                    {
                        'type': 'text',
                        'text': f"""이 의뢰서에서 다음 필드의 값을 읽어주세요:
{chr(10).join(field_descriptions)}

JSON 객체로 반환. 값이 없으면 빈 문자열.{correction_hint}

예: {{"companyName": "바이오푸드랩", "phone": "031-123-4567"}}
JSON만 반환하세요."""
                    }
                ]
            }]
        )

        text = message.content[0].text.strip()
        if text.startswith('```'):
            text = re.sub(r'^```(?:json)?\s*', '', text)
            text = re.sub(r'\s*```$', '', text)
        return json.loads(text)
    except Exception as e:
        print(f'[OCR] Claude 보정 실패: {e}')
        return {}


def _fallback_to_claude_ocr(payload):
    """템플릿 OCR 실패 시 기존 Clova+Claude 방식으로 폴백"""
    # 기존 inspection-form 엔드포인트 로직 재사용
    from flask import make_response
    with app.test_request_context(
        '/api/ocr/inspection-form',
        method='POST',
        json=payload,
        content_type='application/json'
    ):
        return ocr_inspection_form()


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

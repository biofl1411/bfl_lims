#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BFL LIMS - OCR 프록시 서버
Naver Clova OCR API를 브라우저에서 호출할 수 있도록 프록시 역할.
CORS 문제를 해결하고 Secret Key를 서버 측에 보관.

실행: python ocr_proxy.py
포트: 5002

엔드포인트:
  POST /api/ocr/biz-license   — 사업자등록증 OCR (Document OCR)
  POST /api/ocr/general        — 인허가 문서 등 일반 OCR (General OCR)
  GET  /api/ocr/health         — 서버 상태 확인
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import time
import os

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
    print(f'BFL OCR Proxy Server starting on port {port}')
    print(f'  biz-license OCR: POST http://localhost:{port}/api/ocr/biz-license')
    print(f'  general OCR:     POST http://localhost:{port}/api/ocr/general')
    print(f'  health check:    GET  http://localhost:{port}/api/ocr/health')
    app.run(host='0.0.0.0', port=port, debug=True)

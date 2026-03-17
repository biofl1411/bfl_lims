#!/usr/bin/env python3
"""
토스페이먼츠 API 프록시 서버
- 시크릿 키를 서버에서 관리하여 클라이언트 노출 방지
- /toss/transactions: 기간별 거래 내역 조회
- /toss/settlements: 정산 내역 (수수료 포함) 조회
- /toss/config: 시크릿 키 설정/확인
"""

import os
import sys
import json
import base64
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

TOSS_API_BASE = 'https://api.tosspayments.com'
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.toss_config.json')


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_config(data):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_auth_header():
    config = load_config()
    secret_key = config.get('secret_key', '')
    if not secret_key:
        return None
    # Basic Auth: base64(secret_key:)
    encoded = base64.b64encode((secret_key + ':').encode()).decode()
    return {'Authorization': f'Basic {encoded}'}


@app.route('/toss/config', methods=['GET'])
def get_config():
    """시크릿 키 설정 여부 확인 (키 자체는 반환하지 않음)"""
    config = load_config()
    has_key = bool(config.get('secret_key', ''))
    return jsonify({
        'configured': has_key,
        'keyPrefix': config.get('secret_key', '')[:12] + '...' if has_key else '',
        'lastUpdated': config.get('updated_at', '')
    })


@app.route('/toss/config', methods=['POST'])
def set_config():
    """시크릿 키 설정"""
    data = request.get_json()
    secret_key = data.get('secret_key', '').strip()
    if not secret_key:
        return jsonify({'error': '시크릿 키를 입력하세요'}), 400

    # 키 유효성 테스트
    encoded = base64.b64encode((secret_key + ':').encode()).decode()
    try:
        resp = requests.get(
            f'{TOSS_API_BASE}/v1/transactions',
            headers={'Authorization': f'Basic {encoded}'},
            params={
                'startDate': datetime.now().strftime('%Y-%m-%dT00:00:00'),
                'endDate': datetime.now().strftime('%Y-%m-%dT23:59:59')
            },
            timeout=15
        )
        if resp.status_code == 401:
            return jsonify({'error': '인증 실패 - 시크릿 키가 올바르지 않습니다'}), 401
    except Exception as e:
        return jsonify({'error': f'연결 테스트 실패: {str(e)}'}), 500

    config = load_config()
    config['secret_key'] = secret_key
    config['updated_at'] = datetime.now().isoformat()
    save_config(config)

    return jsonify({'success': True, 'message': '시크릿 키 설정 완료'})


@app.route('/toss/transactions', methods=['GET'])
def get_transactions():
    """기간별 거래 내역 조회"""
    auth = get_auth_header()
    if not auth:
        return jsonify({'error': '토스페이먼츠 시크릿 키가 설정되지 않았습니다'}), 401

    start_date = request.args.get('startDate', '')
    end_date = request.args.get('endDate', '')

    if not start_date or not end_date:
        return jsonify({'error': 'startDate, endDate 필수'}), 400

    # 시간이 없으면 추가
    if 'T' not in start_date:
        start_date += 'T00:00:00'
    if 'T' not in end_date:
        end_date += 'T23:59:59'

    all_transactions = []
    starting_after = request.args.get('startingAfter', '')

    # 페이지네이션으로 전체 조회 (최대 10페이지)
    for _ in range(10):
        params = {'startDate': start_date, 'endDate': end_date}
        if starting_after:
            params['startingAfter'] = starting_after

        try:
            resp = requests.get(
                f'{TOSS_API_BASE}/v1/transactions',
                headers=auth,
                params=params,
                timeout=60
            )
            if resp.status_code != 200:
                error_data = resp.json() if resp.headers.get('content-type', '').startswith('application/json') else {}
                return jsonify({
                    'error': f'토스 API 오류 ({resp.status_code})',
                    'detail': error_data.get('message', resp.text[:200])
                }), resp.status_code

            data = resp.json()
            if not data or not isinstance(data, list) or len(data) == 0:
                break

            all_transactions.extend(data)
            # 마지막 transactionKey로 다음 페이지
            starting_after = data[-1].get('transactionKey', '')
            if len(data) < 100:  # 100건 미만이면 마지막 페이지
                break

        except requests.Timeout:
            return jsonify({'error': '토스 API 타임아웃 (60초 초과)'}), 504
        except Exception as e:
            return jsonify({'error': f'요청 실패: {str(e)}'}), 500

    # 입금(결제) 건만 필터링 + 포맷 변환
    deposits = []
    for tx in all_transactions:
        amount = tx.get('amount', 0)
        if amount <= 0:
            continue  # 취소/환불 건 제외

        status = tx.get('status', '')
        if status in ['CANCELED', 'PARTIAL_CANCELED']:
            continue

        deposits.append({
            'paymentKey': tx.get('paymentKey', ''),
            'transactionKey': tx.get('transactionKey', ''),
            'orderId': tx.get('orderId', ''),
            'orderName': tx.get('orderName', ''),
            'amount': amount,
            'status': status,
            'method': tx.get('method', ''),
            'transactionAt': tx.get('transactionAt', ''),
            'cardCompany': tx.get('cardCompany', ''),
            'cardNumber': tx.get('cardNumber', ''),
        })

    return jsonify({
        'count': len(deposits),
        'totalCount': len(all_transactions),
        'deposits': deposits
    })


@app.route('/toss/settlements', methods=['GET'])
def get_settlements():
    """정산 내역 조회 (수수료 포함)"""
    auth = get_auth_header()
    if not auth:
        return jsonify({'error': '토스페이먼츠 시크릿 키가 설정되지 않았습니다'}), 401

    start_date = request.args.get('startDate', '')
    end_date = request.args.get('endDate', '')
    page = request.args.get('page', '1')
    size = request.args.get('size', '100')

    if not start_date or not end_date:
        return jsonify({'error': 'startDate, endDate 필수'}), 400

    try:
        resp = requests.get(
            f'{TOSS_API_BASE}/v1/settlements',
            headers=auth,
            params={
                'startDate': start_date,
                'endDate': end_date,
                'page': page,
                'size': size
            },
            timeout=60
        )
        if resp.status_code != 200:
            error_data = resp.json() if resp.headers.get('content-type', '').startswith('application/json') else {}
            return jsonify({
                'error': f'토스 API 오류 ({resp.status_code})',
                'detail': error_data.get('message', resp.text[:200])
            }), resp.status_code

        return jsonify(resp.json())

    except Exception as e:
        return jsonify({'error': f'요청 실패: {str(e)}'}), 500


@app.route('/toss/payment/<payment_key>', methods=['GET'])
def get_payment(payment_key):
    """개별 결제 상세 조회"""
    auth = get_auth_header()
    if not auth:
        return jsonify({'error': '시크릿 키 미설정'}), 401

    try:
        resp = requests.get(
            f'{TOSS_API_BASE}/v1/payments/{payment_key}',
            headers=auth,
            timeout=15
        )
        if resp.status_code != 200:
            return jsonify({'error': f'조회 실패 ({resp.status_code})'}), resp.status_code
        return jsonify(resp.json())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/toss/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'service': 'toss_proxy', 'port': 5004})


if __name__ == '__main__':
    print('[토스 프록시] 포트 5004에서 시작...')
    app.run(host='0.0.0.0', port=5004, debug=False)

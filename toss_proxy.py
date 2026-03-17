#!/usr/bin/env python3
"""
토스페이먼츠 API 프록시 서버 (다중 MID 지원)
- 시크릿 키를 서버에서 관리하여 클라이언트 노출 방지
- /toss/transactions: 기간별 거래 내역 조회 (mid 파라미터로 상점 선택)
- /toss/settlements: 정산 내역 (수수료 포함) 조회
- /toss/config: 시크릿 키 설정/확인 (다중 MID)
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

# 상점 아이디 목록
MIDS = {
    'bioflw9bnm': '바이오푸드랩',
    'link_bioflc7qd': '바이오푸드랩(링크)'
}


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_config(data):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_auth_header(mid=None):
    """특정 MID의 시크릿 키로 인증 헤더 생성"""
    config = load_config()
    keys = config.get('keys', {})

    # mid 지정 시 해당 키 사용
    if mid and mid in keys:
        secret_key = keys[mid].get('secret_key', '')
    else:
        # 하위 호환: 기존 단일 키
        secret_key = config.get('secret_key', '')
        # keys에서 첫번째 키 사용
        if not secret_key and keys:
            first_mid = list(keys.keys())[0]
            secret_key = keys[first_mid].get('secret_key', '')

    if not secret_key:
        return None
    encoded = base64.b64encode((secret_key + ':').encode()).decode()
    return {'Authorization': f'Basic {encoded}'}


@app.route('/toss/config', methods=['GET'])
def get_config():
    """다중 MID 설정 상태 확인"""
    config = load_config()
    keys = config.get('keys', {})

    # 하위 호환: 기존 단일 키가 있으면 포함
    if not keys and config.get('secret_key'):
        result = {
            'configured': True,
            'mids': MIDS,
            'keys': {
                'default': {
                    'configured': True,
                    'keyPrefix': config['secret_key'][:12] + '...',
                    'label': '기본',
                    'lastUpdated': config.get('updated_at', '')
                }
            }
        }
        return jsonify(result)

    result = {
        'configured': any(k.get('secret_key') for k in keys.values()) if keys else False,
        'mids': MIDS,
        'keys': {}
    }

    for mid, label in MIDS.items():
        if mid in keys and keys[mid].get('secret_key'):
            sk = keys[mid]['secret_key']
            result['keys'][mid] = {
                'configured': True,
                'keyPrefix': sk[:12] + '...',
                'label': label,
                'lastUpdated': keys[mid].get('updated_at', '')
            }
        else:
            result['keys'][mid] = {
                'configured': False,
                'keyPrefix': '',
                'label': label,
                'lastUpdated': ''
            }

    return jsonify(result)


@app.route('/toss/config', methods=['POST'])
def set_config():
    """특정 MID의 시크릿 키 설정"""
    data = request.get_json()
    secret_key = data.get('secret_key', '').strip()
    mid = data.get('mid', '').strip()

    if not secret_key:
        return jsonify({'error': '시크릿 키를 입력하세요'}), 400
    if not mid:
        return jsonify({'error': '상점 아이디(MID)를 지정하세요'}), 400

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
    if 'keys' not in config:
        config['keys'] = {}
    config['keys'][mid] = {
        'secret_key': secret_key,
        'updated_at': datetime.now().isoformat()
    }
    save_config(config)

    label = MIDS.get(mid, mid)
    return jsonify({'success': True, 'message': f'{label} 시크릿 키 설정 완료'})


def _fetch_transactions_for_mid(mid, start_date, end_date):
    """특정 MID의 거래 내역 조회"""
    auth = get_auth_header(mid)
    if not auth:
        return [], f'{MIDS.get(mid, mid)} 시크릿 키 미설정'

    all_transactions = []
    starting_after = ''

    for _ in range(10):
        params = {'startDate': start_date, 'endDate': end_date}
        if starting_after:
            params['startingAfter'] = starting_after

        resp = requests.get(
            f'{TOSS_API_BASE}/v1/transactions',
            headers=auth,
            params=params,
            timeout=60
        )
        if resp.status_code != 200:
            error_data = resp.json() if resp.headers.get('content-type', '').startswith('application/json') else {}
            return [], f'토스 API 오류 ({resp.status_code}): {error_data.get("message", resp.text[:200])}'

        data = resp.json()
        if not data or not isinstance(data, list) or len(data) == 0:
            break

        all_transactions.extend(data)
        starting_after = data[-1].get('transactionKey', '')
        if len(data) < 100:
            break

    return all_transactions, None


@app.route('/toss/transactions', methods=['GET'])
def get_transactions():
    """기간별 거래 내역 조회 (mid 파라미터: 특정 MID 또는 'all')"""
    start_date = request.args.get('startDate', '')
    end_date = request.args.get('endDate', '')
    mid = request.args.get('mid', 'all')

    if not start_date or not end_date:
        return jsonify({'error': 'startDate, endDate 필수'}), 400

    if 'T' not in start_date:
        start_date += 'T00:00:00'
    if 'T' not in end_date:
        end_date += 'T23:59:59'

    config = load_config()
    keys = config.get('keys', {})

    # 조회할 MID 목록
    if mid == 'all':
        target_mids = [m for m in MIDS.keys() if m in keys and keys[m].get('secret_key')]
        if not target_mids:
            # 하위 호환: 기존 단일 키
            if config.get('secret_key'):
                auth = get_auth_header()
                if auth:
                    target_mids = ['_default']
            if not target_mids:
                return jsonify({'error': '설정된 시크릿 키가 없습니다'}), 401
    else:
        target_mids = [mid]

    all_transactions = []
    errors = []

    for m in target_mids:
        if m == '_default':
            # 하위 호환 모드
            auth = get_auth_header()
            txs = []
            starting_after = ''
            for _ in range(10):
                params = {'startDate': start_date, 'endDate': end_date}
                if starting_after:
                    params['startingAfter'] = starting_after
                try:
                    resp = requests.get(f'{TOSS_API_BASE}/v1/transactions', headers=auth, params=params, timeout=60)
                    if resp.status_code != 200:
                        break
                    data = resp.json()
                    if not data or not isinstance(data, list) or len(data) == 0:
                        break
                    txs.extend(data)
                    starting_after = data[-1].get('transactionKey', '')
                    if len(data) < 100:
                        break
                except:
                    break
            for tx in txs:
                tx['_mid'] = 'default'
                tx['_midLabel'] = '기본'
            all_transactions.extend(txs)
        else:
            try:
                txs, err = _fetch_transactions_for_mid(m, start_date, end_date)
                if err:
                    errors.append(err)
                else:
                    for tx in txs:
                        tx['_mid'] = m
                        tx['_midLabel'] = MIDS.get(m, m)
                    all_transactions.extend(txs)
            except requests.Timeout:
                errors.append(f'{MIDS.get(m, m)} 타임아웃')
            except Exception as e:
                errors.append(f'{MIDS.get(m, m)}: {str(e)}')

    # 입금(결제) 건만 필터링
    deposits = []
    for tx in all_transactions:
        amount = tx.get('amount', 0)
        if amount <= 0:
            continue
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
            'mid': tx.get('_mid', ''),
            'midLabel': tx.get('_midLabel', ''),
        })

    result = {
        'count': len(deposits),
        'totalCount': len(all_transactions),
        'deposits': deposits
    }
    if errors:
        result['errors'] = errors

    return jsonify(result)


@app.route('/toss/settlements', methods=['GET'])
def get_settlements():
    """정산 내역 조회 (수수료 포함)"""
    mid = request.args.get('mid', '')
    auth = get_auth_header(mid if mid else None)
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
    mid = request.args.get('mid', '')
    auth = get_auth_header(mid if mid else None)
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
    print('[토스 프록시] 포트 5004에서 시작 (다중 MID 지원)...')
    app.run(host='0.0.0.0', port=5004, debug=False)

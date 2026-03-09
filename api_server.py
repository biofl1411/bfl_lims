#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BioFoodLab 식약처 수집 트리거 서버
- 수동 수집 실행만 담당 (데이터 조회는 Firestore 직접 사용)
- 프론트엔드에서 POST /api/admin/collect 호출 시 collector.py 실행

실행: python3 api_server.py
포트: 5003 (기본)
"""

import os
import json
import subprocess
import requests as req_lib
from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # GitHub Pages에서 호출 허용


# ============================================================
# 수동 수집 트리거
# ============================================================

@app.route('/api/admin/collect', methods=['POST'])
def trigger_collect():
    """수동 수집 실행 (백그라운드)"""
    data = request.get_json() or {}
    mode = data.get('mode', 'incremental')
    apis = data.get('apis', [])

    install_dir = os.path.dirname(os.path.abspath(__file__))
    cmd = ['/usr/bin/python3', os.path.join(install_dir, 'collector.py')]

    if mode == 'full':
        cmd.append('--full')
    elif mode == 'auto':
        cmd.append('--auto')
    elif mode == 'resume':
        cmd.append('--resume')
    if apis:
        cmd.extend(apis)

    try:
        # 환경변수 로드
        env = os.environ.copy()
        env_file = os.path.join(install_dir, '.env')
        if os.path.exists(env_file):
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        line = line.replace('export ', '')
                        k, v = line.split('=', 1)
                        env[k.strip()] = v.strip()

        log_file = os.path.join(install_dir, 'logs', 'manual.log')
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        with open(log_file, 'a') as lf:
            subprocess.Popen(cmd, env=env, stdout=lf, stderr=lf)

        return jsonify({
            'success': True,
            'message': f'수집 시작 (mode={mode}, apis={len(apis)}개)',
            'log_file': log_file
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# ============================================================
# Claude AI 프록시 (브라우저 CORS 우회용)
# POST /api/claude  →  Anthropic API 중계
# ============================================================

ANTHROPIC_API_URL = 'https://api.anthropic.com/v1/messages'
ANTHROPIC_VERSION = '2023-06-01'

def _load_env():
    """프로젝트 .env 에서 환경변수 로드"""
    env = os.environ.copy()
    env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    line = line.replace('export ', '')
                    k, v = line.split('=', 1)
                    env[k.strip()] = v.strip()
    return env

@app.route('/api/claude', methods=['POST'])
def claude_proxy():
    """
    Anthropic API 프록시.
    브라우저에서 직접 호출하면 CORS 차단되므로 서버가 중계.
    .env 파일의 ANTHROPIC_API_KEY 사용.
    """
    env = _load_env()
    api_key = env.get('ANTHROPIC_API_KEY', '')
    if not api_key:
        return jsonify({'error': 'ANTHROPIC_API_KEY가 .env에 없습니다'}), 500

    body = request.get_json(force=True)
    if not body:
        return jsonify({'error': '요청 본문이 없습니다'}), 400

    # model 강제 지정 (비용 제어)
    body.setdefault('model', 'claude-sonnet-4-20250514')
    body.setdefault('max_tokens', 3000)

    headers = {
        'x-api-key': api_key,
        'anthropic-version': ANTHROPIC_VERSION,
        'content-type': 'application/json',
    }

    try:
        resp = req_lib.post(ANTHROPIC_API_URL, json=body, headers=headers, timeout=120)
        return Response(resp.content, status=resp.status_code,
                        mimetype='application/json')
    except req_lib.exceptions.Timeout:
        return jsonify({'error': 'Anthropic API 타임아웃 (120s)'}), 504
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================
# 헬스 체크
# ============================================================

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'success': True, 'status': 'ok', 'storage': 'firestore'})


if __name__ == '__main__':
    port = int(os.environ.get('FSS_API_PORT', 5003))
    app.run(host='0.0.0.0', port=port, debug=False)

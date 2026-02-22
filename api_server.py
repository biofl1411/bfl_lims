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
from flask import Flask, request, jsonify
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
# 헬스 체크
# ============================================================

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'success': True, 'status': 'ok', 'storage': 'firestore'})


if __name__ == '__main__':
    port = int(os.environ.get('FSS_API_PORT', 5003))
    app.run(host='0.0.0.0', port=port, debug=False)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BioFoodLab 식약처 데이터 API 서버
- 업체조회 프론트엔드에서 DB 직접 조회
- 지역 드릴다운, 업체명 검색, 제품/원재료 검색 지원

실행: python3 api_server.py
포트: 5050 (기본)
"""

import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql

app = Flask(__name__)
CORS(app)  # GitHub Pages에서 호출 허용

DB_CONFIG = {
    'host': os.environ.get('FSS_DB_HOST', 'localhost'),
    'port': int(os.environ.get('FSS_DB_PORT', 3306)),
    'user': os.environ.get('FSS_DB_USER', 'fss_user'),
    'password': os.environ.get('FSS_DB_PASS', 'your_password_here'),
    'database': os.environ.get('FSS_DB_NAME', 'fss_data'),
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor,
}

API_NAMES = {
    'I1220': '식품제조가공업', 'I2829': '즉석판매제조가공업',
    'I-0020': '건강기능식품제조업', 'I1300': '축산물가공업',
    'I1320': '축산물식육포장처리업', 'I2835': '식육즉석판매가공업',
    'I2831': '식품소분업', 'C001': '수입식품등영업신고',
    'I1260': '식품등수입판매업',
}

def get_db():
    return pymysql.connect(**DB_CONFIG)


# ============================================================
# 1. 업소 검색 (지역 드릴다운 + 키워드)
# ============================================================

@app.route('/api/businesses', methods=['GET'])
def search_businesses():
    """
    업소 검색
    파라미터:
      sido      - 시도 (경기도, 서울특별시 등)
      sigungu   - 시군구 (파주시, 강남구 등)
      dong      - 읍면동 (문산읍 등)
      keyword   - 업체명 키워드 검색
      induty    - 업종 필터
      api_source - API 소스 필터 (I1220 등)
      page      - 페이지 (기본 1)
      size      - 페이지 크기 (기본 50, 최대 200)
    """
    sido = request.args.get('sido', '').strip()
    sigungu = request.args.get('sigungu', '').strip()
    dong = request.args.get('dong', '').strip()
    keyword = request.args.get('keyword', '').strip()
    induty = request.args.get('induty', '').strip()
    api_source = request.args.get('api_source', '').strip()
    page = max(1, int(request.args.get('page', 1)))
    size = min(200, max(1, int(request.args.get('size', 50))))

    conditions = []
    params = []

    if sido:
        conditions.append('addr_sido = %s')
        params.append(sido)
    if sigungu:
        conditions.append('addr_sigungu = %s')
        params.append(sigungu)
    if dong:
        conditions.append('addr_dong = %s')
        params.append(dong)
    if keyword:
        conditions.append('bssh_nm LIKE %s')
        params.append(f'%{keyword}%')
    if induty:
        conditions.append('induty_nm LIKE %s')
        params.append(f'%{induty}%')
    if api_source:
        conditions.append('api_source = %s')
        params.append(api_source)

    where = 'WHERE ' + ' AND '.join(conditions) if conditions else ''
    offset = (page - 1) * size

    conn = get_db()
    try:
        cursor = conn.cursor()

        # 총 건수
        cursor.execute(f'SELECT COUNT(*) as total FROM fss_businesses {where}', params)
        total = cursor.fetchone()['total']

        # 데이터 조회
        cursor.execute(f"""
            SELECT api_source, lcns_no, bssh_nm, prsdnt_nm, induty_nm,
                   prms_dt, telno, locp_addr, instt_nm, clsbiz_dvs_nm,
                   addr_sido, addr_sigungu, addr_dong
            FROM fss_businesses {where}
            ORDER BY bssh_nm
            LIMIT %s OFFSET %s
        """, params + [size, offset])
        rows = cursor.fetchall()

        # API 이름 추가
        for r in rows:
            r['api_name'] = API_NAMES.get(r['api_source'], r['api_source'])

        return jsonify({
            'success': True,
            'total': total,
            'page': page,
            'size': size,
            'pages': (total + size - 1) // size,
            'data': rows
        })
    finally:
        conn.close()


# ============================================================
# 2. 지역 통계 (드릴다운용)
# ============================================================

@app.route('/api/region/stats', methods=['GET'])
def region_stats():
    """
    지역별 업소 수 통계
    파라미터:
      level - sido / sigungu / dong
      sido  - 시도 (sigungu, dong 레벨 시 필수)
      sigungu - 시군구 (dong 레벨 시 필수)
    """
    level = request.args.get('level', 'sido')
    sido = request.args.get('sido', '').strip()
    sigungu = request.args.get('sigungu', '').strip()

    conn = get_db()
    try:
        cursor = conn.cursor()

        if level == 'sido':
            cursor.execute("""
                SELECT addr_sido as name, COUNT(*) as count
                FROM fss_businesses
                WHERE addr_sido IS NOT NULL
                GROUP BY addr_sido
                ORDER BY count DESC
            """)
        elif level == 'sigungu' and sido:
            cursor.execute("""
                SELECT addr_sigungu as name, COUNT(*) as count
                FROM fss_businesses
                WHERE addr_sido = %s AND addr_sigungu IS NOT NULL
                GROUP BY addr_sigungu
                ORDER BY count DESC
            """, (sido,))
        elif level == 'dong' and sido and sigungu:
            cursor.execute("""
                SELECT addr_dong as name, COUNT(*) as count
                FROM fss_businesses
                WHERE addr_sido = %s AND addr_sigungu = %s AND addr_dong IS NOT NULL
                GROUP BY addr_dong
                ORDER BY count DESC
            """, (sido, sigungu))
        else:
            return jsonify({'success': False, 'error': 'Invalid parameters'})

        return jsonify({
            'success': True,
            'level': level,
            'data': cursor.fetchall()
        })
    finally:
        conn.close()


# ============================================================
# 3. 제품 검색
# ============================================================

@app.route('/api/products', methods=['GET'])
def search_products():
    """
    제품 검색
    파라미터:
      keyword    - 제품명 검색
      lcns_no    - 인허가번호로 해당 업소 제품 조회
      bssh_nm    - 업소명
      prdlst_dcnm - 품목유형
      page / size
    """
    keyword = request.args.get('keyword', '').strip()
    lcns_no = request.args.get('lcns_no', '').strip()
    bssh_nm = request.args.get('bssh_nm', '').strip()
    prdlst_dcnm = request.args.get('prdlst_dcnm', '').strip()
    page = max(1, int(request.args.get('page', 1)))
    size = min(200, max(1, int(request.args.get('size', 50))))

    conditions = []
    params = []

    if keyword:
        conditions.append('prdlst_nm LIKE %s')
        params.append(f'%{keyword}%')
    if lcns_no:
        conditions.append('lcns_no = %s')
        params.append(lcns_no)
    if bssh_nm:
        conditions.append('bssh_nm LIKE %s')
        params.append(f'%{bssh_nm}%')
    if prdlst_dcnm:
        conditions.append('prdlst_dcnm LIKE %s')
        params.append(f'%{prdlst_dcnm}%')

    where = 'WHERE ' + ' AND '.join(conditions) if conditions else ''
    offset = (page - 1) * size

    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute(f'SELECT COUNT(*) as total FROM fss_products {where}', params)
        total = cursor.fetchone()['total']

        cursor.execute(f"""
            SELECT api_source, lcns_no, bssh_nm, prdlst_report_no,
                   prdlst_nm, prdlst_dcnm, prms_dt, production,
                   pog_daycnt, induty_cd_nm
            FROM fss_products {where}
            ORDER BY prms_dt DESC
            LIMIT %s OFFSET %s
        """, params + [size, offset])

        return jsonify({
            'success': True,
            'total': total,
            'page': page,
            'data': cursor.fetchall()
        })
    finally:
        conn.close()


# ============================================================
# 4. 원재료 검색
# ============================================================

@app.route('/api/materials', methods=['GET'])
def search_materials():
    """
    원재료 검색
    파라미터:
      keyword       - 원재료명 검색
      prdlst_report_no - 품목제조번호로 조회
      lcns_no       - 인허가번호
      page / size
    """
    keyword = request.args.get('keyword', '').strip()
    report_no = request.args.get('prdlst_report_no', '').strip()
    lcns_no = request.args.get('lcns_no', '').strip()
    page = max(1, int(request.args.get('page', 1)))
    size = min(200, max(1, int(request.args.get('size', 50))))

    conditions = []
    params = []

    if keyword:
        conditions.append('rawmtrl_nm LIKE %s')
        params.append(f'%{keyword}%')
    if report_no:
        conditions.append('prdlst_report_no = %s')
        params.append(report_no)
    if lcns_no:
        conditions.append('lcns_no = %s')
        params.append(lcns_no)

    where = 'WHERE ' + ' AND '.join(conditions) if conditions else ''
    offset = (page - 1) * size

    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute(f'SELECT COUNT(*) as total FROM fss_materials {where}', params)
        total = cursor.fetchone()['total']

        cursor.execute(f"""
            SELECT api_source, lcns_no, bssh_nm, prdlst_report_no,
                   prdlst_nm, prdlst_dcnm, rawmtrl_nm, rawmtrl_ordno
            FROM fss_materials {where}
            ORDER BY prdlst_report_no, CAST(rawmtrl_ordno AS UNSIGNED)
            LIMIT %s OFFSET %s
        """, params + [size, offset])

        return jsonify({
            'success': True,
            'total': total,
            'page': page,
            'data': cursor.fetchall()
        })
    finally:
        conn.close()


# ============================================================
# 5. 변경 이력 조회
# ============================================================

@app.route('/api/changes', methods=['GET'])
def search_changes():
    """
    인허가 변경 이력
    파라미터:
      lcns_no  - 인허가번호
      bssh_nm  - 업소명
      page / size
    """
    lcns_no = request.args.get('lcns_no', '').strip()
    bssh_nm = request.args.get('bssh_nm', '').strip()
    page = max(1, int(request.args.get('page', 1)))
    size = min(100, max(1, int(request.args.get('size', 20))))

    conditions = []
    params = []

    if lcns_no:
        conditions.append('lcns_no = %s')
        params.append(lcns_no)
    if bssh_nm:
        conditions.append('bssh_nm LIKE %s')
        params.append(f'%{bssh_nm}%')

    if not conditions:
        return jsonify({'success': False, 'error': '검색 조건을 입력하세요 (lcns_no 또는 bssh_nm)'})

    where = 'WHERE ' + ' AND '.join(conditions)
    offset = (page - 1) * size

    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute(f'SELECT COUNT(*) as total FROM fss_changes {where}', params)
        total = cursor.fetchone()['total']

        cursor.execute(f"""
            SELECT * FROM fss_changes {where}
            ORDER BY chng_dt DESC
            LIMIT %s OFFSET %s
        """, params + [size, offset])

        return jsonify({
            'success': True,
            'total': total,
            'page': page,
            'data': cursor.fetchall()
        })
    finally:
        conn.close()


# ============================================================
# 6. 수집 현황
# ============================================================

@app.route('/api/status', methods=['GET'])
def collection_status():
    """수집 현황 조회"""
    conn = get_db()
    try:
        cursor = conn.cursor()

        # 테이블별 건수
        stats = {}
        for tbl in ['fss_businesses', 'fss_products', 'fss_materials', 'fss_changes']:
            cursor.execute(f'SELECT COUNT(*) as cnt, MAX(collected_at) as last_dt FROM {tbl}')
            row = cursor.fetchone()
            stats[tbl] = {
                'count': row['cnt'],
                'last_collected': str(row['last_dt']) if row['last_dt'] else None
            }

        # 최근 수집 로그
        cursor.execute("""
            SELECT * FROM fss_collect_log
            ORDER BY started_at DESC LIMIT 20
        """)
        logs = cursor.fetchall()
        for l in logs:
            l['started_at'] = str(l['started_at'])
            l['finished_at'] = str(l['finished_at']) if l['finished_at'] else None

        return jsonify({
            'success': True,
            'tables': stats,
            'recent_logs': logs
        })
    finally:
        conn.close()


@app.route('/api/collect/detail', methods=['GET'])
def collect_detail():
    """API별 수집 상세 현황 (API 갱신 페이지용)"""
    ALL_APIS = {
        'I1220':  {'name': '식품제조가공업', 'table': 'fss_businesses'},
        'I2829':  {'name': '즉석판매제조가공업', 'table': 'fss_businesses'},
        'I-0020': {'name': '건강기능식품 전문/벤처제조업', 'table': 'fss_businesses'},
        'I1300':  {'name': '축산물 가공업', 'table': 'fss_businesses'},
        'I1320':  {'name': '축산물 식육포장처리업', 'table': 'fss_businesses'},
        'I2835':  {'name': '식육즉석판매가공업', 'table': 'fss_businesses'},
        'I2831':  {'name': '식품소분업', 'table': 'fss_businesses'},
        'C001':   {'name': '수입식품등영업신고', 'table': 'fss_businesses'},
        'I1260':  {'name': '식품등수입판매업', 'table': 'fss_businesses'},
        'I1250':  {'name': '식품(첨가물)품목제조보고', 'table': 'fss_products'},
        'I1310':  {'name': '축산물 품목제조정보', 'table': 'fss_products'},
        'C002':   {'name': '식품(첨가물)품목제조보고(원재료)', 'table': 'fss_materials'},
        'C003':   {'name': '건강기능식품 품목제조신고(원재료)', 'table': 'fss_materials'},
        'C006':   {'name': '축산물품목제조보고(원재료)', 'table': 'fss_materials'},
        'I2859':  {'name': '식품업소 인허가 변경 정보', 'table': 'fss_changes'},
        'I2860':  {'name': '건강기능식품업소 인허가 변경 정보', 'table': 'fss_changes'},
    }

    conn = get_db()
    try:
        cursor = conn.cursor()
        result = []

        for sid, info in ALL_APIS.items():
            # DB 건수
            cursor.execute(
                f"SELECT COUNT(*) as cnt FROM {info['table']} WHERE api_source=%s",
                (sid,))
            row = cursor.fetchone()
            db_count = row['cnt'] if row else 0

            # 최근 수집 로그
            cursor.execute("""
                SELECT collect_type, fetched_count, inserted_count, updated_count,
                       error_count, error_msg, started_at, finished_at, duration_sec,
                       total_count
                FROM fss_collect_log
                WHERE api_source=%s
                ORDER BY started_at DESC LIMIT 1
            """, (sid,))
            last_log = cursor.fetchone()

            api_data = {
                'api_source': sid,
                'name': info['name'],
                'table': info['table'],
                'db_count': db_count,
                'last_api_total': last_log['total_count'] if last_log else None,
                'last_collect': None,
            }

            if last_log:
                api_data['last_collect'] = {
                    'type': last_log['collect_type'],
                    'fetched': last_log['fetched_count'],
                    'inserted': last_log['inserted_count'],
                    'updated': last_log['updated_count'],
                    'errors': last_log['error_count'],
                    'error_msg': last_log['error_msg'],
                    'started_at': str(last_log['started_at']),
                    'finished_at': str(last_log['finished_at']) if last_log['finished_at'] else None,
                    'duration_sec': last_log['duration_sec'],
                }

            # 상태 판단
            if db_count == 0 and (not last_log or last_log['total_count'] is None):
                api_data['status'] = 'not_started'
            elif last_log and last_log['total_count'] and db_count < last_log['total_count']:
                api_data['status'] = 'in_progress'
            else:
                api_data['status'] = 'completed'

            result.append(api_data)

        return jsonify({'success': True, 'apis': result})
    finally:
        conn.close()


# ============================================================
# 7. 업종 목록 (필터용)
# ============================================================

@app.route('/api/industries', methods=['GET'])
def get_industries():
    """등록된 업종 목록"""
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT induty_nm, COUNT(*) as count
            FROM fss_businesses
            WHERE induty_nm IS NOT NULL AND induty_nm != ''
            GROUP BY induty_nm
            ORDER BY count DESC
        """)
        return jsonify({'success': True, 'data': cursor.fetchall()})
    finally:
        conn.close()


# ============================================================
# 8. 관리자 - 설정 조회/저장
# ============================================================

@app.route('/api/admin/settings', methods=['GET'])
def get_admin_settings():
    """수집 설정 조회"""
    conn = get_db()
    try:
        cursor = conn.cursor()

        # 스케줄 설정
        schedule = None
        try:
            cursor.execute('SELECT * FROM fss_schedule_config WHERE id=1')
            schedule = cursor.fetchone()
            if schedule and 'updated_at' in schedule:
                schedule['updated_at'] = str(schedule['updated_at'])
            # Decimal → float 변환
            if schedule and 'request_delay' in schedule:
                schedule['request_delay'] = float(schedule['request_delay'])
        except Exception:
            schedule = {
                'collect_hour': 3, 'collect_minute': 0,
                'collect_mode': 'incremental', 'is_active': 1,
                'api_key': 'e5a1d9f07d6c4424a757',
                'batch_size': 100, 'request_delay': 0.3
            }

        # API 설정
        apis = []
        try:
            cursor.execute('SELECT * FROM fss_api_config ORDER BY api_source')
            apis = cursor.fetchall()
            for a in apis:
                if 'updated_at' in a and a['updated_at']:
                    a['updated_at'] = str(a['updated_at'])
                if 'last_collected' in a and a['last_collected']:
                    a['last_collected'] = str(a['last_collected'])
        except Exception:
            pass

        return jsonify({
            'success': True,
            'schedule': schedule,
            'apis': apis
        })
    finally:
        conn.close()


@app.route('/api/admin/settings', methods=['POST'])
def save_admin_settings():
    """수집 설정 저장"""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'No data'})

    conn = get_db()
    try:
        cursor = conn.cursor()

        # 스케줄 저장
        if 'schedule' in data:
            s = data['schedule']
            cursor.execute("""
                INSERT INTO fss_schedule_config
                    (id, collect_hour, collect_minute, collect_mode,
                     is_active, api_key, batch_size, request_delay)
                VALUES (1, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    collect_hour = VALUES(collect_hour),
                    collect_minute = VALUES(collect_minute),
                    collect_mode = VALUES(collect_mode),
                    is_active = VALUES(is_active),
                    api_key = VALUES(api_key),
                    batch_size = VALUES(batch_size),
                    request_delay = VALUES(request_delay)
            """, (
                s.get('collect_hour', 3),
                s.get('collect_minute', 0),
                s.get('collect_mode', 'incremental'),
                s.get('is_active', 1),
                s.get('api_key', ''),
                s.get('batch_size', 100),
                s.get('request_delay', 0.3),
            ))

            # cron 업데이트
            update_cron(s.get('collect_hour', 3), s.get('collect_minute', 0), s.get('is_active', 1))

        # API 설정 저장
        if 'apis' in data:
            for api_id, api_cfg in data['apis'].items():
                enabled_fields = json.dumps(api_cfg.get('fields', []), ensure_ascii=False)
                all_fields = json.dumps(api_cfg.get('all_fields', []), ensure_ascii=False)

                cursor.execute("""
                    INSERT INTO fss_api_config
                        (api_source, api_name, category, is_enabled, enabled_fields, all_fields)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        api_name = VALUES(api_name),
                        category = VALUES(category),
                        is_enabled = VALUES(is_enabled),
                        enabled_fields = VALUES(enabled_fields),
                        all_fields = VALUES(all_fields)
                """, (
                    api_id,
                    api_cfg.get('name', ''),
                    api_cfg.get('category', ''),
                    1 if api_cfg.get('enabled', True) else 0,
                    enabled_fields,
                    all_fields,
                ))

        conn.commit()
        return jsonify({'success': True, 'message': '설정이 저장되었습니다.'})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)})
    finally:
        conn.close()


def update_cron(hour, minute, is_active):
    """crontab 업데이트"""
    import subprocess
    install_dir = os.path.dirname(os.path.abspath(__file__))
    cron_cmd = f'{minute} {hour} * * * cd {install_dir} && source .env && /usr/bin/python3 collector.py >> logs/cron.log 2>&1'

    try:
        # 기존 crontab 읽기
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        existing = result.stdout if result.returncode == 0 else ''

        # collector.py 관련 라인 제거
        lines = [l for l in existing.strip().split('\n') if l and 'collector.py' not in l]

        # 활성화된 경우에만 추가
        if is_active:
            lines.append(cron_cmd)

        new_cron = '\n'.join(lines) + '\n'
        proc = subprocess.run(['crontab', '-'], input=new_cron, capture_output=True, text=True)

        if proc.returncode == 0:
            app.logger.info(f'Cron 업데이트: {hour:02d}:{minute:02d} (active={is_active})')
        else:
            app.logger.warning(f'Cron 업데이트 실패: {proc.stderr}')
    except Exception as e:
        app.logger.warning(f'Cron 업데이트 오류: {e}')


# ============================================================
# 9. 관리자 - 수동 수집 트리거
# ============================================================

@app.route('/api/admin/collect', methods=['POST'])
def trigger_collect():
    """수동 수집 실행 (백그라운드)"""
    import subprocess
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
        # 백그라운드로 실행
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
# 10. 관리자 페이지 서빙
# ============================================================

@app.route('/admin')
def admin_page():
    """관리자 페이지"""
    admin_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'admin_api_settings.html')
    if os.path.exists(admin_file):
        from flask import send_file
        return send_file(admin_file)
    return '관리자 페이지 파일이 없습니다.', 404


@app.route('/admin/collect')
def admin_collect_page():
    """API 갱신 현황 페이지"""
    collect_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'admin_collect_status.html')
    if os.path.exists(collect_file):
        from flask import send_file
        return send_file(collect_file)
    return 'API 갱신 현황 페이지 파일이 없습니다.', 404


# ============================================================
# 8. 수집 설정 관리
# ============================================================

SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.json')

def load_settings():
    """설정 파일 로드"""
    defaults = {
        'collectTime': '03:00',
        'collectMode': 'incremental',
        'serverUrl': 'http://localhost:5050',
        'activeApis': [
            'I1220','I2829','I-0020','I1300','I1320','I2835','I2831','C001','I1260',
            'I1250','I1310','C002','C003','C006','I2859','I2860'
        ]
    }
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                saved = json.load(f)
                defaults.update(saved)
    except Exception:
        pass
    return defaults

def save_settings(data):
    """설정 파일 저장"""
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def update_crontab(collect_time):
    """crontab 수집 시각 업데이트"""
    try:
        hour, minute = collect_time.split(':')
        hour = int(hour)
        minute = int(minute)
        install_dir = os.path.dirname(os.path.abspath(__file__))

        cron_cmd = (f'{minute} {hour} * * * '
                    f'cd {install_dir} && source .env && '
                    f'/usr/bin/python3 collector.py >> logs/cron.log 2>&1')

        # 기존 crontab에서 collector.py 라인 제거 후 새로 추가
        import subprocess
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        existing = result.stdout if result.returncode == 0 else ''
        lines = [l for l in existing.strip().split('\n') if l and 'collector.py' not in l]
        lines.append(cron_cmd)
        new_cron = '\n'.join(lines) + '\n'
        subprocess.run(['crontab', '-'], input=new_cron, text=True, check=True)
        return True
    except Exception as e:
        print(f'Crontab 업데이트 실패: {e}')
        return False


@app.route('/api/settings', methods=['GET'])
def get_settings():
    """현재 설정 조회"""
    return jsonify({'success': True, 'data': load_settings()})


@app.route('/api/settings', methods=['POST'])
def post_settings():
    """설정 저장 + crontab 업데이트"""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': '요청 데이터 없음'})

    try:
        save_settings(data)

        # crontab 시각 업데이트
        cron_ok = False
        if 'collectTime' in data:
            cron_ok = update_crontab(data['collectTime'])

        # collector.py용 설정 파일도 업데이트
        collector_conf = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'collect_config.json')
        with open(collector_conf, 'w', encoding='utf-8') as f:
            json.dump({
                'active_apis': data.get('activeApis', []),
                'collect_mode': data.get('collectMode', 'incremental'),
                'collect_time': data.get('collectTime', '03:00'),
            }, f, ensure_ascii=False, indent=2)

        return jsonify({
            'success': True,
            'message': '설정 저장 완료',
            'crontab_updated': cron_ok
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


if __name__ == '__main__':
    port = int(os.environ.get('FSS_API_PORT', 5050))
    app.run(host='0.0.0.0', port=port, debug=False)

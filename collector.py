#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BioFoodLab 식약처 인허가 데이터 수집기
- 매일 새벽 3시(KST) cron 실행
- 16개 API에서 전국 데이터 수집 → MariaDB 저장
- 주소 파싱으로 시도/시군구/읍면동 인덱싱

사용법:
  python3 collector.py              # 증분 수집 (어제 변경분만)
  python3 collector.py --full       # 전체 수집 (최초 실행 시)
  python3 collector.py --full I1220 # 특정 API만 전체 수집
  python3 collector.py --resume     # 이어서 수집 (중단된 지점부터)
  python3 collector.py --auto       # 자동 모드 (미완료→이어서, 완료→증분) ★ cron용
  python3 collector.py --status     # 수집 현황 확인
"""

import os
import sys
import json
import time
import re
import logging
import argparse
from datetime import datetime, timedelta
from urllib.request import urlopen, Request
from urllib.parse import quote
from urllib.error import URLError, HTTPError

import pymysql

# ============================================================
# 설정
# ============================================================

DB_CONFIG = {
    'host': os.environ.get('FSS_DB_HOST', 'localhost'),
    'port': int(os.environ.get('FSS_DB_PORT', 3306)),
    'user': os.environ.get('FSS_DB_USER', 'fss_user'),
    'password': os.environ.get('FSS_DB_PASS', 'your_password_here'),
    'database': os.environ.get('FSS_DB_NAME', 'fss_data'),
    'charset': 'utf8mb4',
    'autocommit': False,
}

API_KEY = os.environ.get('FSS_API_KEY', 'e5a1d9f07d6c4424a757')
BASE_URL = 'https://openapi.foodsafetykorea.go.kr/api'
BATCH_SIZE = 100  # API 1회 요청당 최대 건수
REQUEST_DELAY = 0.3  # API 요청 간격(초) - 서버 부하 방지

# ============================================================
# API 정의
# ============================================================

# 카테고리별 API 목록
BUSINESS_APIS = {
    'I1220':  {'name': '식품제조가공업',              'table': 'fss_businesses'},
    'I2829':  {'name': '즉석판매제조가공업',          'table': 'fss_businesses'},
    'I-0020': {'name': '건강기능식품 전문/벤처제조업', 'table': 'fss_businesses'},
    'I1300':  {'name': '축산물 가공업',               'table': 'fss_businesses'},
    'I1320':  {'name': '축산물 식육포장처리업',       'table': 'fss_businesses'},
    'I2835':  {'name': '식육즉석판매가공업',          'table': 'fss_businesses'},
    'I2831':  {'name': '식품소분업',                  'table': 'fss_businesses'},
    'C001':   {'name': '수입식품등영업신고',          'table': 'fss_businesses'},
    'I1260':  {'name': '식품등수입판매업',            'table': 'fss_businesses'},
}

PRODUCT_APIS = {
    'I1250':  {'name': '식품(첨가물)품목제조보고',    'table': 'fss_products'},
    'I1310':  {'name': '축산물 품목제조정보',         'table': 'fss_products'},
}

MATERIAL_APIS = {
    'C002':   {'name': '식품(첨가물)품목제조보고(원재료)', 'table': 'fss_materials'},
    'C003':   {'name': '건강기능식품 품목제조신고(원재료)', 'table': 'fss_materials'},
    'C006':   {'name': '축산물품목제조보고(원재료)',       'table': 'fss_materials'},
}

CHANGE_APIS = {
    'I2859':  {'name': '식품업소 인허가 변경 정보',         'table': 'fss_changes'},
    'I2860':  {'name': '건강기능식품업소 인허가 변경 정보', 'table': 'fss_changes'},
}

ALL_APIS = {**BUSINESS_APIS, **PRODUCT_APIS, **MATERIAL_APIS, **CHANGE_APIS}

# ============================================================
# 로깅 설정
# ============================================================

LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(
            os.path.join(LOG_DIR, f'collect_{datetime.now().strftime("%Y%m%d")}.log'),
            encoding='utf-8'
        ),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================
# 주소 파싱
# ============================================================

def parse_address(addr):
    """주소 문자열에서 시도/시군구/읍면동 추출"""
    if not addr:
        return None, None, None

    addr = addr.strip()
    parts = addr.split()
    if not parts:
        return None, None, None

    sido = parts[0]  # "경기도", "서울특별시" 등
    sigungu = parts[1] if len(parts) > 1 else None
    dong = None

    if len(parts) > 2:
        # 3번째 요소가 읍/면/동/리/가인 경우
        p2 = parts[2]
        if re.search(r'(읍|면|동|리|가)$', p2):
            dong = p2
        # "OO로", "OO길" 등 도로명은 건너뜀

    return sido, sigungu, dong

# ============================================================
# API 호출
# ============================================================

# 한도 초과 상태 플래그
_quota_exceeded = False

def fetch_api(service_id, start, end, chng_dt=None):
    """식약처 API 호출 → JSON 파싱
    
    Returns:
        (total, rows, status)
        status: 'ok', 'empty', 'quota_exceeded', 'error'
    """
    global _quota_exceeded

    # 이미 한도 초과 상태면 요청하지 않음
    if _quota_exceeded:
        return 0, [], 'quota_exceeded'

    url = f'{BASE_URL}/{API_KEY}/{service_id}/json/{start}/{end}'
    if chng_dt:
        url += f'/CHNG_DT={chng_dt}'

    try:
        req = Request(url, headers={'User-Agent': 'BioFoodLab-Collector/1.0'})
        with urlopen(req, timeout=30) as resp:
            raw = resp.read()

        # 제어문자 제거 (일부 API 응답에 포함)
        text = raw.decode('utf-8', errors='replace')
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', text)

        data = json.loads(text)
        key = list(data.keys())[0]
        result = data[key]

        # 오류 체크
        if 'RESULT' in result:
            code = result['RESULT'].get('CODE', '')
            msg = result['RESULT'].get('MSG', '')

            if code == 'INFO-300':
                # 호출 한도 초과
                logger.warning(f'  ⚠️ API 호출 한도 초과! ({msg})')
                _quota_exceeded = True
                return 0, [], 'quota_exceeded'

            if code == 'INFO-200':
                # 해당 데이터 없음
                return 0, [], 'empty'

            if code.startswith('ERROR'):
                logger.warning(f'  API 오류 ({service_id}): [{code}] {msg}')
                return 0, [], 'error'

        # total_count 안전 파싱
        tc = result.get('total_count', 0)
        total = int(tc) if tc != '' and tc is not None else 0

        rows = result.get('row', [])
        return total, rows, 'ok'

    except (json.JSONDecodeError, KeyError) as e:
        logger.warning(f'  JSON 파싱 오류 ({service_id} {start}-{end}): {e}')
        return 0, [], 'error'
    except (URLError, HTTPError, TimeoutError) as e:
        logger.warning(f'  네트워크 오류 ({service_id} {start}-{end}): {e}')
        return 0, [], 'error'
    except Exception as e:
        logger.error(f'  예상치 못한 오류 ({service_id} {start}-{end}): {e}')
        return 0, [], 'error'

# ============================================================
# DB 저장
# ============================================================

def upsert_business(cursor, api_source, row):
    """업소 인허가 UPSERT"""
    addr = row.get('LOCP_ADDR', '')
    sido, sigungu, dong = parse_address(addr)

    sql = """
    INSERT INTO fss_businesses
        (api_source, lcns_no, bssh_nm, prsdnt_nm, induty_nm, prms_dt,
         telno, locp_addr, instt_nm, clsbiz_dvs_nm,
         addr_sido, addr_sigungu, addr_dong)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        bssh_nm = VALUES(bssh_nm),
        prsdnt_nm = VALUES(prsdnt_nm),
        induty_nm = VALUES(induty_nm),
        prms_dt = VALUES(prms_dt),
        telno = VALUES(telno),
        locp_addr = VALUES(locp_addr),
        instt_nm = VALUES(instt_nm),
        clsbiz_dvs_nm = VALUES(clsbiz_dvs_nm),
        addr_sido = VALUES(addr_sido),
        addr_sigungu = VALUES(addr_sigungu),
        addr_dong = VALUES(addr_dong)
    """
    cursor.execute(sql, (
        api_source,
        row.get('LCNS_NO', ''),
        row.get('BSSH_NM', ''),
        row.get('PRSDNT_NM'),
        row.get('INDUTY_NM'),
        row.get('PRMS_DT'),
        row.get('TELNO'),
        addr,
        row.get('INSTT_NM'),
        row.get('CLSBIZ_DVS_NM'),
        sido, sigungu, dong
    ))
    return cursor.rowcount  # 1=INSERT, 2=UPDATE


def upsert_product(cursor, api_source, row):
    """품목 제조 보고 UPSERT"""
    report_no = row.get('PRDLST_REPORT_NO', '')
    if not report_no:
        return 0

    sql = """
    INSERT INTO fss_products
        (api_source, lcns_no, bssh_nm, prdlst_report_no, prms_dt,
         prdlst_nm, prdlst_dcnm, production, hieng_lntrt_dvs_nm,
         child_crtfc_yn, pog_daycnt, induty_cd_nm, dispos, shap,
         stdr_stnd, ntk_mthd, primary_fnclty, iftkn_atnt_matr_cn,
         cstdy_mthd, prdt_shap_cd_nm, usage_info, prpos,
         frmlc_mtrqlt, qlity_mntnc, etqty_xport, last_updt_dtm)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    ON DUPLICATE KEY UPDATE
        lcns_no = VALUES(lcns_no),
        bssh_nm = VALUES(bssh_nm),
        prms_dt = VALUES(prms_dt),
        prdlst_nm = VALUES(prdlst_nm),
        prdlst_dcnm = VALUES(prdlst_dcnm),
        production = VALUES(production),
        pog_daycnt = VALUES(pog_daycnt),
        last_updt_dtm = VALUES(last_updt_dtm)
    """
    cursor.execute(sql, (
        api_source,
        row.get('LCNS_NO', ''),
        row.get('BSSH_NM'),
        report_no,
        row.get('PRMS_DT'),
        row.get('PRDLST_NM'),
        row.get('PRDLST_DCNM'),
        row.get('PRODUCTION'),
        row.get('HIENG_LNTRT_DVS_NM'),
        row.get('CHILD_CRTFC_YN'),
        row.get('POG_DAYCNT'),
        row.get('INDUTY_CD_NM'),
        row.get('DISPOS'),
        row.get('SHAP'),
        row.get('STDR_STND'),
        row.get('NTK_MTHD'),
        row.get('PRIMARY_FNCLTY'),
        row.get('IFTKN_ATNT_MATR_CN'),
        row.get('CSTDY_MTHD'),
        row.get('PRDT_SHAP_CD_NM'),
        row.get('USAGE'),
        row.get('PRPOS'),
        row.get('FRMLC_MTRQLT'),
        row.get('QLITY_MNTNC_TMLMT_DAYCNT'),
        row.get('ETQTY_XPORT_PRDLST_YN'),
        row.get('LAST_UPDT_DTM'),
    ))
    return cursor.rowcount


def upsert_material(cursor, api_source, row):
    """원재료 정보 UPSERT"""
    report_no = row.get('PRDLST_REPORT_NO', '')
    ordno = row.get('RAWMTRL_ORDNO', '0')
    if not report_no:
        return 0

    sql = """
    INSERT INTO fss_materials
        (api_source, lcns_no, bssh_nm, prdlst_report_no, prms_dt,
         prdlst_nm, prdlst_dcnm, rawmtrl_nm, rawmtrl_ordno,
         chng_dt, etqty_xport)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    ON DUPLICATE KEY UPDATE
        lcns_no = VALUES(lcns_no),
        bssh_nm = VALUES(bssh_nm),
        prdlst_nm = VALUES(prdlst_nm),
        rawmtrl_nm = VALUES(rawmtrl_nm),
        chng_dt = VALUES(chng_dt)
    """
    cursor.execute(sql, (
        api_source,
        row.get('LCNS_NO'),
        row.get('BSSH_NM'),
        report_no,
        row.get('PRMS_DT'),
        row.get('PRDLST_NM'),
        row.get('PRDLST_DCNM'),
        row.get('RAWMTRL_NM'),
        ordno,
        row.get('CHNG_DT'),
        row.get('ETQTY_XPORT_PRDLST_YN'),
    ))
    return cursor.rowcount


def insert_change(cursor, api_source, row):
    """변경 이력 INSERT (중복 허용)"""
    sql = """
    INSERT INTO fss_changes
        (api_source, lcns_no, bssh_nm, induty_cd_nm, telno,
         site_addr, chng_dt, chng_bf_cn, chng_af_cn, chng_prvns)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """
    cursor.execute(sql, (
        api_source,
        row.get('LCNS_NO', ''),
        row.get('BSSH_NM'),
        row.get('INDUTY_CD_NM'),
        row.get('TELNO'),
        row.get('SITE_ADDR'),
        row.get('CHNG_DT'),
        row.get('CHNG_BF_CN'),
        row.get('CHNG_AF_CN'),
        row.get('CHNG_PRVNS'),
    ))
    return 1

# ============================================================
# DB에서 기존 수집 건수 확인
# ============================================================

def get_collected_count(conn, service_id, table):
    """해당 API의 DB 저장 건수 조회"""
    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE api_source=%s", (service_id,))
        count = cursor.fetchone()[0]
        cursor.close()
        return count
    except Exception:
        return 0

# ============================================================
# 수집 메인 로직
# ============================================================

def collect_api(conn, service_id, api_info, collect_type='incremental',
                chng_dt=None, resume=False):
    """단일 API 전체 수집
    
    resume=True이면 DB에 이미 저장된 건수 이후부터 수집
    """
    global _quota_exceeded

    table = api_info['table']
    name = api_info['name']

    # 이미 한도 초과 상태면 건너뜀
    if _quota_exceeded:
        logger.info(f'⏭️ [{service_id}] {name} — 한도 초과로 건너뜀')
        return 'quota_exceeded'

    started_at = datetime.now()
    logger.info(f'▶ [{service_id}] {name} 수집 시작 ({collect_type})')

    # 1단계: 총 건수 확인
    dt_param = chng_dt if collect_type == 'incremental' and chng_dt else None
    total, _, status = fetch_api(service_id, 1, 1, dt_param)

    if status == 'quota_exceeded':
        logger.warning(f'  ⏭️ 한도 초과 — 이 API 건너뜀')
        log_collection(conn, service_id, name, collect_type, 0, 0, 0, 0, 0,
                       'API 호출 한도 초과 (INFO-300)', started_at)
        return 'quota_exceeded'

    if total == 0:
        logger.info(f'  → 데이터 없음 (0건)')
        log_collection(conn, service_id, name, collect_type, 0, 0, 0, 0, 0, None, started_at)
        return 'empty'

    # resume 모드: 이미 수집된 건수 확인 후 시작 지점 결정
    start_from = 1
    if resume:
        already = get_collected_count(conn, service_id, table)
        if already >= total:
            logger.info(f'  ✅ 이미 완료: DB {already:,}건 / API {total:,}건')
            log_collection(conn, service_id, name, collect_type + '_resume',
                           total, 0, 0, 0, 0, '이미 수집 완료', started_at)
            return 'already_done'
        elif already > 0:
            start_from = already + 1
            logger.info(f'  🔄 이어서 수집: DB {already:,}건 보유 → {start_from:,}번부터 시작 (총 {total:,}건)')
        else:
            logger.info(f'  총 {total:,}건 수집 예정')
    else:
        logger.info(f'  총 {total:,}건 수집 예정')

    # 2단계: 페이지네이션으로 수집
    fetched = 0
    inserted = 0
    updated = 0
    errors = 0
    error_msg = None

    cursor = conn.cursor()

    try:
        for start in range(start_from, total + 1, BATCH_SIZE):
            end = min(start + BATCH_SIZE - 1, total)
            _, rows, status = fetch_api(service_id, start, end, dt_param)

            # 한도 초과 감지 → 여기까지 저장하고 중단
            if status == 'quota_exceeded':
                logger.warning(f'  ⚠️ {fetched:,}건까지 수집 후 한도 초과로 중단')
                conn.commit()
                error_msg = f'API 한도 초과 — {start_from}~{start-1}번 수집 완료'
                break

            if not rows:
                time.sleep(REQUEST_DELAY)
                continue

            for row in rows:
                try:
                    if table == 'fss_businesses':
                        rc = upsert_business(cursor, service_id, row)
                    elif table == 'fss_products':
                        rc = upsert_product(cursor, service_id, row)
                    elif table == 'fss_materials':
                        rc = upsert_material(cursor, service_id, row)
                    elif table == 'fss_changes':
                        rc = insert_change(cursor, service_id, row)
                    else:
                        continue

                    if rc == 1:
                        inserted += 1
                    elif rc == 2:
                        updated += 1
                    fetched += 1

                except pymysql.Error as e:
                    errors += 1
                    if errors <= 5:
                        logger.warning(f'  DB 오류: {e} / row={row.get("LCNS_NO", "?")}')
                    if not error_msg:
                        error_msg = str(e)

            # 배치 커밋 (100건마다)
            conn.commit()

            # 진행률 로그 (1000건마다)
            total_fetched = (start_from - 1) + fetched if resume else fetched
            if fetched > 0 and fetched % 1000 < BATCH_SIZE:
                pct = (total_fetched / total * 100) if total else 0
                logger.info(f'  진행: {total_fetched:,}/{total:,} ({pct:.1f}%) 입력={inserted} 갱신={updated}')

            time.sleep(REQUEST_DELAY)

        conn.commit()

    except Exception as e:
        logger.error(f'  수집 중 오류: {e}')
        error_msg = str(e)
        conn.rollback()
    finally:
        cursor.close()

    elapsed = (datetime.now() - started_at).total_seconds()
    result_status = 'quota_exceeded' if _quota_exceeded else 'ok'

    if result_status == 'ok':
        logger.info(f'  ✅ 완료: {fetched:,}건 (입력={inserted}, 갱신={updated}, 오류={errors}) [{elapsed:.0f}초]')
    else:
        logger.info(f'  ⏸️ 중단: {fetched:,}건 저장됨 (입력={inserted}, 갱신={updated}) [{elapsed:.0f}초]')

    log_collection(conn, service_id, name,
                   collect_type + ('_resume' if resume else ''),
                   total, fetched, inserted, updated, errors, error_msg, started_at)

    return result_status


def collect_api_auto(conn, service_id, api_info):
    """자동 모드: 미완료 API는 이어서 수집, 완료된 API는 증분 수집
    
    1) API 총 건수 확인
    2) DB 건수와 비교
    3) DB < API → resume (이어서 수집)
    4) DB >= API → incremental (어제 변경분만)
    """
    global _quota_exceeded

    if _quota_exceeded:
        logger.info(f'⏭️ [{service_id}] {api_info["name"]} — 한도 초과로 건너뜀')
        return 'quota_exceeded'

    table = api_info['table']
    name = api_info['name']

    # 1) API 총 건수 확인 (전체 모드)
    api_total, _, status = fetch_api(service_id, 1, 1, None)

    if status == 'quota_exceeded':
        return 'quota_exceeded'

    # 2) DB 건수 확인
    db_count = get_collected_count(conn, service_id, table)

    # 3) 판단: 미완료 vs 완료
    if api_total > 0 and db_count < api_total:
        # 미완료 → resume 모드 (전체 수집 이어서)
        pct = (db_count / api_total * 100) if api_total else 0
        logger.info(f'📊 [{service_id}] {name}: DB {db_count:,} / API {api_total:,} ({pct:.1f}%) → 이어서 수집')
        return collect_api(conn, service_id, api_info,
                          collect_type='full', chng_dt=None, resume=True)
    else:
        # 완료 → 증분 수집 (어제 변경분만)
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
        logger.info(f'✅ [{service_id}] {name}: DB {db_count:,} / API {api_total:,} — 증분 수집 ({yesterday})')
        return collect_api(conn, service_id, api_info,
                          collect_type='incremental', chng_dt=yesterday, resume=False)


def log_collection(conn, api_source, api_name, collect_type,
                   total, fetched, inserted, updated, errors, error_msg, started_at):
    """수집 로그 기록"""
    finished_at = datetime.now()
    duration = int((finished_at - started_at).total_seconds())
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO fss_collect_log
                (api_source, api_name, collect_type, total_count, fetched_count,
                 inserted_count, updated_count, error_count, error_msg,
                 started_at, finished_at, duration_sec)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (api_source, api_name, collect_type, total, fetched,
              inserted, updated, errors, error_msg,
              started_at, finished_at, duration))
        conn.commit()
        cursor.close()
    except Exception as e:
        logger.error(f'로그 기록 실패: {e}')

# ============================================================
# 수집 현황
# ============================================================

def show_status(conn):
    """현재 DB 수집 현황 출력"""
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    print('\n' + '='*70)
    print('  식약처 데이터 수집 현황')
    print('='*70)

    # 테이블별 건수
    tables = [
        ('fss_businesses', '업소 인허가'),
        ('fss_products', '품목 제조'),
        ('fss_materials', '원재료'),
        ('fss_changes', '변경 이력'),
    ]
    print(f'\n{"테이블":<20} {"건수":>12} {"최신수집":>20}')
    print('-'*55)
    for tbl, name in tables:
        try:
            cursor.execute(f'SELECT COUNT(*) as cnt, MAX(collected_at) as last_dt FROM {tbl}')
            row = cursor.fetchone()
            cnt = f"{row['cnt']:,}" if row['cnt'] else '0'
            last = str(row['last_dt'])[:16] if row['last_dt'] else '-'
            print(f'{name:<20} {cnt:>12} {last:>20}')
        except:
            print(f'{name:<20} {"(테이블없음)":>12}')

    # API별 건수
    print(f'\n{"API":<10} {"이름":<25} {"DB건수":>10} {"상태":>8}')
    print('-'*60)
    for sid, info in ALL_APIS.items():
        try:
            cursor.execute(f"SELECT COUNT(*) as cnt FROM {info['table']} WHERE api_source=%s", (sid,))
            row = cursor.fetchone()
            cnt = row['cnt']
            cnt_str = f"{cnt:,}"
            status = '✅' if cnt > 0 else '⬜'
        except:
            cnt_str = '-'
            status = '❌'
        print(f'{sid:<10} {info["name"]:<25} {cnt_str:>10} {status:>8}')

    # 최근 수집 로그
    print(f'\n최근 수집 이력:')
    print('-'*70)
    try:
        cursor.execute("""
            SELECT api_source, api_name, collect_type, fetched_count,
                   inserted_count, updated_count, error_count, error_msg,
                   started_at, duration_sec
            FROM fss_collect_log
            ORDER BY started_at DESC LIMIT 10
        """)
        for r in cursor.fetchall():
            dt = str(r['started_at'])[:16]
            err_info = f" ⚠️{r['error_msg'][:30]}" if r['error_msg'] else ''
            print(f"  {dt} [{r['api_source']}] {r['api_name']} "
                  f"({r['collect_type']}) {r['fetched_count']:,}건 "
                  f"(+{r['inserted_count']}/↻{r['updated_count']}/✗{r['error_count']})"
                  f" {r['duration_sec']}초{err_info}")
    except:
        print('  (로그 없음)')

    print()
    cursor.close()

# ============================================================
# 메인
# ============================================================

def load_schedule_config(conn):
    """DB에서 스케줄 설정 읽기"""
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT * FROM fss_schedule_config WHERE id=1')
        row = cursor.fetchone()
        cursor.close()
        return row
    except Exception:
        return None


def load_api_configs(conn):
    """DB에서 API 설정 읽기"""
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT api_source, is_enabled, enabled_fields FROM fss_api_config')
        rows = cursor.fetchall()
        cursor.close()
        return rows if rows else None
    except Exception:
        return None


def main():
    global _quota_exceeded

    parser = argparse.ArgumentParser(description='식약처 인허가 데이터 수집기')
    parser.add_argument('--full', action='store_true', help='전체 수집 (최초 실행)')
    parser.add_argument('--resume', action='store_true', help='이어서 수집 (중단된 지점부터)')
    parser.add_argument('--auto', action='store_true', help='자동 모드 (미완료→이어서, 완료→증분) cron용')
    parser.add_argument('--status', action='store_true', help='수집 현황 확인')
    parser.add_argument('apis', nargs='*', help='특정 API만 수집 (예: I1220 I2829)')
    args = parser.parse_args()

    # DB 연결
    try:
        conn = pymysql.connect(**DB_CONFIG)
        logger.info(f'DB 연결 성공: {DB_CONFIG["host"]}:{DB_CONFIG["port"]}/{DB_CONFIG["database"]}')
    except pymysql.Error as e:
        logger.error(f'DB 연결 실패: {e}')
        sys.exit(1)

    try:
        if args.status:
            show_status(conn)
            return

        # ─── DB에서 설정 읽기 ───
        db_schedule = load_schedule_config(conn)
        db_api_configs = load_api_configs(conn)

        # DB 설정이 있으면 적용
        global API_KEY, BATCH_SIZE, REQUEST_DELAY
        if db_schedule:
            if db_schedule.get('api_key'):
                API_KEY = db_schedule['api_key']
            if db_schedule.get('batch_size'):
                BATCH_SIZE = int(db_schedule['batch_size'])
            if db_schedule.get('request_delay'):
                REQUEST_DELAY = float(db_schedule['request_delay'])
            logger.info(f'DB 설정 로드: batch={BATCH_SIZE}, delay={REQUEST_DELAY}s')

        # resume이면 항상 full 모드
        if args.resume:
            collect_type = 'full'
        elif args.auto:
            collect_type = 'auto'
        else:
            collect_type = 'full' if args.full else (
                db_schedule.get('collect_mode', 'incremental') if db_schedule else 'incremental'
            )

        # 증분 수집: 어제 날짜 기준
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
        chng_dt = yesterday if collect_type not in ('full', 'auto') else None

        # 수집 대상 결정
        if args.apis:
            # 명령줄 인자 우선
            targets = {k: v for k, v in ALL_APIS.items() if k in args.apis}
            if not targets:
                logger.error(f'유효하지 않은 API: {args.apis}')
                logger.info(f'사용 가능한 API: {list(ALL_APIS.keys())}')
                return
        elif db_api_configs:
            # DB 설정에서 활성화된 API만
            enabled_ids = [c['api_source'] for c in db_api_configs if c.get('is_enabled')]
            targets = {k: v for k, v in ALL_APIS.items() if k in enabled_ids}
            if not targets:
                logger.warning('DB 설정에 활성화된 API가 없습니다. 전체 API로 진행합니다.')
                targets = ALL_APIS
            else:
                logger.info(f'DB 설정 기준: {len(targets)}개 API 활성')
        else:
            targets = ALL_APIS

        logger.info(f'{"="*60}')
        logger.info(f'식약처 데이터 수집 시작 ({collect_type}{"+ resume" if args.resume else ""})')
        logger.info(f'대상: {len(targets)}개 API')
        logger.info(f'설정: batch_size={BATCH_SIZE}, delay={REQUEST_DELAY}s')
        if chng_dt:
            logger.info(f'변경일자 기준: {chng_dt} 이후')
        logger.info(f'{"="*60}')

        total_start = time.time()
        _quota_exceeded = False  # 초기화

        # 수집 순서: 업소 → 품목 → 원재료 → 변경이력
        order = list(BUSINESS_APIS.keys()) + list(PRODUCT_APIS.keys()) + \
                list(MATERIAL_APIS.keys()) + list(CHANGE_APIS.keys())

        completed = []
        skipped = []

        for sid in order:
            if sid in targets:
                if collect_type == 'auto':
                    # 자동 모드: API별로 미완료/완료 판단하여 수집
                    result = collect_api_auto(conn, sid, targets[sid])
                else:
                    result = collect_api(conn, sid, targets[sid], collect_type,
                                         chng_dt, resume=args.resume)
                if result == 'quota_exceeded':
                    skipped.append(sid)
                else:
                    completed.append(sid)

        elapsed = time.time() - total_start
        logger.info(f'{"="*60}')
        logger.info(f'수집 종료! 총 소요시간: {elapsed:.0f}초 ({elapsed/60:.1f}분)')
        logger.info(f'  완료: {len(completed)}개 API {completed}')
        if skipped:
            logger.info(f'  ⏭️ 한도초과 건너뜀: {len(skipped)}개 API {skipped}')
            logger.info(f'  → 내일 자동 수집 시 이어서 진행됩니다 (--auto)')
        logger.info(f'{"="*60}')

        show_status(conn)

    finally:
        conn.close()


if __name__ == '__main__':
    main()

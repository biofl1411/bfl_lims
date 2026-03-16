#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BioFoodLab 식약처 인허가 데이터 수집기 (Firestore 버전)
- 매일 새벽 3시(KST) cron 실행
- 16개 API에서 전국 데이터 수집 → Firestore 저장
- 주소 파싱으로 시도/시군구/읍면동 인덱싱
- 무료 티어 쓰기 제한 준수 (18,000건/일)

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

import firebase_admin
from firebase_admin import credentials, firestore

# ============================================================
# 설정
# ============================================================

SERVICE_ACCOUNT_KEY = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'serviceAccountKey.json'
)

API_KEY = os.environ.get('FSS_API_KEY', 'e5a1d9f07d6c4424a757')
BASE_URL = 'https://openapi.foodsafetykorea.go.kr/api'
BATCH_SIZE = 1000  # API 1회 요청당 최대 건수 (식약처 API 최대 1000건)
REQUEST_DELAY = 0.3  # API 요청 간격(초) - 서버 부하 방지

# Firestore 무료 티어 쓰기 제한
DAILY_WRITE_LIMIT = 18000  # 20,000 중 여유 2,000

# ============================================================
# API 정의
# ============================================================

BUSINESS_APIS = {
    'I1220':  {'name': '식품제조가공업',              'collection': 'fss_businesses'},
    'I2829':  {'name': '즉석판매제조가공업',          'collection': 'fss_businesses'},
    'I-0020': {'name': '건강기능식품 전문/벤처제조업', 'collection': 'fss_businesses'},
    'I1300':  {'name': '축산물 가공업',               'collection': 'fss_businesses'},
    'I1320':  {'name': '축산물 식육포장처리업',       'collection': 'fss_businesses'},
    'I2835':  {'name': '식육즉석판매가공업',          'collection': 'fss_businesses'},
    'I2831':  {'name': '식품소분업',                  'collection': 'fss_businesses'},
    'C001':   {'name': '수입식품등영업신고',          'collection': 'fss_businesses'},
    'I1260':  {'name': '식품등수입판매업',            'collection': 'fss_businesses'},
}

PRODUCT_APIS = {
    'I1250':  {'name': '식품(첨가물)품목제조보고',    'collection': 'fss_products'},
    'I1310':  {'name': '축산물 품목제조정보',         'collection': 'fss_products'},
}

MATERIAL_APIS = {
    'C002':   {'name': '식품(첨가물)품목제조보고(원재료)', 'collection': 'fss_materials'},
    'C003':   {'name': '건강기능식품 품목제조신고(원재료)', 'collection': 'fss_materials'},
    'C006':   {'name': '축산물품목제조보고(원재료)',       'collection': 'fss_materials'},
}

CHANGE_APIS = {
    'I2859':  {'name': '식품업소 인허가 변경 정보',         'collection': 'fss_changes'},
    'I2860':  {'name': '건강기능식품업소 인허가 변경 정보', 'collection': 'fss_changes'},
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
# Firestore 초기화
# ============================================================

fdb = None

def init_firestore():
    global fdb
    if not os.path.exists(SERVICE_ACCOUNT_KEY):
        logger.error(f'서비스 계정 키 파일이 없습니다: {SERVICE_ACCOUNT_KEY}')
        sys.exit(1)

    cred = credentials.Certificate(SERVICE_ACCOUNT_KEY)
    firebase_admin.initialize_app(cred)
    fdb = firestore.client()
    logger.info('Firestore 연결 성공')

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

    sido = parts[0]
    sigungu = parts[1] if len(parts) > 1 else None
    dong = None

    if len(parts) > 2:
        p2 = parts[2]
        if re.search(r'(읍|면|동|리|가)$', p2):
            dong = p2

    return sido, sigungu, dong

# ============================================================
# API 호출
# ============================================================

_quota_exceeded = False

def fetch_api(service_id, start, end, chng_dt=None, max_retries=3):
    """식약처 API 호출 → JSON 파싱 (실패 시 최대 max_retries회 재시도)"""
    global _quota_exceeded

    if _quota_exceeded:
        return 0, [], 'quota_exceeded'

    url = f'{BASE_URL}/{API_KEY}/{service_id}/json/{start}/{end}'
    if chng_dt:
        url += f'/CHNG_DT={chng_dt}'

    for attempt in range(1, max_retries + 1):
        try:
            req = Request(url, headers={'User-Agent': 'BioFoodLab-Collector/1.0'})
            with urlopen(req, timeout=90) as resp:
                raw = resp.read()

            if not raw or len(raw) == 0:
                if attempt < max_retries:
                    logger.info(f'  빈 응답 ({service_id} {start}-{end}), {attempt}/{max_retries}회 재시도...')
                    time.sleep(1 * attempt)
                    continue
                logger.warning(f'  빈 응답 ({service_id} {start}-{end}), {max_retries}회 실패')
                return 0, [], 'error'

            text = raw.decode('utf-8', errors='replace')
            text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', text)

            data = json.loads(text)
            key = list(data.keys())[0]
            result = data[key]

            if 'RESULT' in result:
                code = result['RESULT'].get('CODE', '')
                msg = result['RESULT'].get('MSG', '')

                if code == 'INFO-300':
                    logger.warning(f'  API 호출 한도 초과! ({msg})')
                    _quota_exceeded = True
                    return 0, [], 'quota_exceeded'

                if code == 'INFO-200':
                    return 0, [], 'empty'

                if code.startswith('ERROR'):
                    logger.warning(f'  API 오류 ({service_id}): [{code}] {msg}')
                    return 0, [], 'error'

            tc = result.get('total_count', 0)
            total = int(tc) if tc != '' and tc is not None else 0

            rows = result.get('row', [])
            return total, rows, 'ok'

        except (json.JSONDecodeError, KeyError) as e:
            if attempt < max_retries:
                logger.info(f'  JSON 파싱 오류 ({service_id} {start}-{end}): {e}, {attempt}/{max_retries}회 재시도...')
                time.sleep(1 * attempt)
                continue
            logger.warning(f'  JSON 파싱 오류 ({service_id} {start}-{end}): {e}, {max_retries}회 실패')
            return 0, [], 'error'
        except (URLError, HTTPError, TimeoutError) as e:
            if attempt < max_retries:
                logger.info(f'  네트워크 오류 ({service_id} {start}-{end}): {e}, {attempt}/{max_retries}회 재시도...')
                time.sleep(2 * attempt)
                continue
            logger.warning(f'  네트워크 오류 ({service_id} {start}-{end}): {e}, {max_retries}회 실패')
            return 0, [], 'error'
        except Exception as e:
            logger.error(f'  예상치 못한 오류 ({service_id} {start}-{end}): {e}')
            return 0, [], 'error'

    return 0, [], 'error'

# ============================================================
# Firestore 저장
# ============================================================

_daily_write_count = 0

def check_write_quota():
    """무료 티어 쓰기 한도 체크"""
    global _daily_write_count
    if _daily_write_count >= DAILY_WRITE_LIMIT:
        logger.warning(f'일일 쓰기 한도 도달 ({DAILY_WRITE_LIMIT}건). 수집 중단.')
        return False
    return True


def detect_new_businesses(rows):
    """페이지 단위로 신규 업소 감지 (get_all 벌크 조회)"""
    lcns_nos = [r.get('LCNS_NO', '') for r in rows if r.get('LCNS_NO')]
    if not lcns_nos:
        return set()

    try:
        doc_refs = [fdb.collection('fss_businesses').document(ln) for ln in lcns_nos]
        existing_docs = fdb.get_all(doc_refs, field_paths=[])
        existing_ids = {doc.id for doc in existing_docs if doc.exists}
        new_ids = set(lcns_nos) - existing_ids
        return new_ids
    except Exception as e:
        logger.warning(f'  신규 업소 감지 실패: {e}')
        return set()


def record_new_business(batch, api_source, row):
    """신규 업소를 fss_new_businesses 컬렉션에 기록"""
    global _daily_write_count
    lcns_no = row.get('LCNS_NO', '')
    if not lcns_no:
        return

    addr = row.get('LOCP_ADDR', '')
    sido, sigungu, dong = parse_address(addr)

    doc_ref = fdb.collection('fss_new_businesses').document(lcns_no)
    batch.set(doc_ref, {
        'api_source': api_source,
        'lcns_no': lcns_no,
        'bssh_nm': row.get('BSSH_NM', ''),
        'prsdnt_nm': row.get('PRSDNT_NM') or '',
        'induty_nm': row.get('INDUTY_NM') or '',
        'prms_dt': row.get('PRMS_DT') or '',
        'telno': row.get('TELNO') or '',
        'locp_addr': addr,
        'instt_nm': row.get('INSTT_NM') or '',
        'clsbiz_dvs_nm': row.get('CLSBIZ_DVS_NM') or '',
        'addr_sido': sido or '',
        'addr_sigungu': sigungu or '',
        'addr_dong': dong or '',
        'detected_at': firestore.SERVER_TIMESTAMP,
    })
    _daily_write_count += 1
    logger.info(f'    🆕 신규 업소 감지: {row.get("BSSH_NM", "")} ({lcns_no})')


def upsert_business(batch, api_source, row, new_ids=None):
    """업소 인허가 Firestore 저장"""
    global _daily_write_count
    if not check_write_quota():
        return 'quota_exceeded'

    lcns_no = row.get('LCNS_NO', '')
    if not lcns_no:
        return 0

    addr = row.get('LOCP_ADDR', '')
    sido, sigungu, dong = parse_address(addr)

    doc_ref = fdb.collection('fss_businesses').document(lcns_no)
    batch.set(doc_ref, {
        'api_source': api_source,
        'lcns_no': lcns_no,
        'bssh_nm': row.get('BSSH_NM', ''),
        'prsdnt_nm': row.get('PRSDNT_NM') or '',
        'induty_nm': row.get('INDUTY_NM') or '',
        'prms_dt': row.get('PRMS_DT') or '',
        'telno': row.get('TELNO') or '',
        'locp_addr': addr,
        'instt_nm': row.get('INSTT_NM') or '',
        'clsbiz_dvs_nm': row.get('CLSBIZ_DVS_NM') or '',
        'addr_sido': sido or '',
        'addr_sigungu': sigungu or '',
        'addr_dong': dong or '',
        'collected_at': firestore.SERVER_TIMESTAMP,
    }, merge=True)
    _daily_write_count += 1

    # 신규 업소 감지 시 fss_new_businesses에도 기록
    if new_ids and lcns_no in new_ids:
        record_new_business(batch, api_source, row)

    return 1


def upsert_product(batch, api_source, row):
    """품목 제조 보고 Firestore 저장"""
    global _daily_write_count
    if not check_write_quota():
        return 'quota_exceeded'

    report_no = row.get('PRDLST_REPORT_NO', '')
    if not report_no:
        return 0

    doc_ref = fdb.collection('fss_products').document(report_no)
    batch.set(doc_ref, {
        'api_source': api_source,
        'lcns_no': row.get('LCNS_NO', ''),
        'bssh_nm': row.get('BSSH_NM') or '',
        'prdlst_report_no': report_no,
        'prms_dt': row.get('PRMS_DT') or '',
        'prdlst_nm': row.get('PRDLST_NM') or '',
        'prdlst_dcnm': row.get('PRDLST_DCNM') or '',
        'production': row.get('PRODUCTION') or '',
        'hieng_lntrt_dvs_nm': row.get('HIENG_LNTRT_DVS_NM') or '',
        'child_crtfc_yn': row.get('CHILD_CRTFC_YN') or '',
        'pog_daycnt': row.get('POG_DAYCNT') or '',
        'induty_cd_nm': row.get('INDUTY_CD_NM') or '',
        'dispos': row.get('DISPOS') or '',
        'shap': row.get('SHAP') or '',
        'stdr_stnd': row.get('STDR_STND') or '',
        'ntk_mthd': row.get('NTK_MTHD') or '',
        'primary_fnclty': row.get('PRIMARY_FNCLTY') or '',
        'iftkn_atnt_matr_cn': row.get('IFTKN_ATNT_MATR_CN') or '',
        'cstdy_mthd': row.get('CSTDY_MTHD') or '',
        'prdt_shap_cd_nm': row.get('PRDT_SHAP_CD_NM') or '',
        'usage_info': row.get('USAGE') or '',
        'prpos': row.get('PRPOS') or '',
        'frmlc_mtrqlt': row.get('FRMLC_MTRQLT') or '',
        'qlity_mntnc': row.get('QLITY_MNTNC_TMLMT_DAYCNT') or '',
        'etqty_xport': row.get('ETQTY_XPORT_PRDLST_YN') or '',
        'last_updt_dtm': row.get('LAST_UPDT_DTM') or '',
        'collected_at': firestore.SERVER_TIMESTAMP,
    }, merge=True)
    _daily_write_count += 1
    return 1


def upsert_material(batch, api_source, row):
    """원재료 정보 Firestore 저장"""
    global _daily_write_count
    if not check_write_quota():
        return 'quota_exceeded'

    report_no = row.get('PRDLST_REPORT_NO', '')
    ordno = str(row.get('RAWMTRL_ORDNO', '0'))
    if not report_no:
        return 0

    doc_id = f'{report_no}_{ordno}'
    doc_ref = fdb.collection('fss_materials').document(doc_id)
    batch.set(doc_ref, {
        'api_source': api_source,
        'lcns_no': row.get('LCNS_NO') or '',
        'bssh_nm': row.get('BSSH_NM') or '',
        'prdlst_report_no': report_no,
        'prms_dt': row.get('PRMS_DT') or '',
        'prdlst_nm': row.get('PRDLST_NM') or '',
        'prdlst_dcnm': row.get('PRDLST_DCNM') or '',
        'rawmtrl_nm': row.get('RAWMTRL_NM') or '',
        'rawmtrl_ordno': ordno,
        'chng_dt': row.get('CHNG_DT') or '',
        'etqty_xport': row.get('ETQTY_XPORT_PRDLST_YN') or '',
        'collected_at': firestore.SERVER_TIMESTAMP,
    }, merge=True)
    _daily_write_count += 1
    return 1


def insert_change(batch, api_source, row):
    """변경 이력 Firestore 저장 (자동 ID)"""
    global _daily_write_count
    if not check_write_quota():
        return 'quota_exceeded'

    doc_ref = fdb.collection('fss_changes').document()
    batch.set(doc_ref, {
        'api_source': api_source,
        'lcns_no': row.get('LCNS_NO', ''),
        'bssh_nm': row.get('BSSH_NM') or '',
        'induty_cd_nm': row.get('INDUTY_CD_NM') or '',
        'telno': row.get('TELNO') or '',
        'site_addr': row.get('SITE_ADDR') or '',
        'chng_dt': row.get('CHNG_DT') or '',
        'chng_bf_cn': row.get('CHNG_BF_CN') or '',
        'chng_af_cn': row.get('CHNG_AF_CN') or '',
        'chng_prvns': row.get('CHNG_PRVNS') or '',
        'collected_at': firestore.SERVER_TIMESTAMP,
    })
    _daily_write_count += 1
    return 1

# ============================================================
# Firestore에서 기존 수집 건수 확인
# ============================================================

def get_collected_count(service_id, collection_name):
    """해당 API의 Firestore 문서 수 조회"""
    try:
        query = fdb.collection(collection_name).where('api_source', '==', service_id)
        # count() 집계 사용 (Firestore v2)
        count_query = query.count()
        results = count_query.get()
        return results[0][0].value if results else 0
    except Exception:
        # count()가 지원되지 않는 경우 fallback
        try:
            docs = fdb.collection(collection_name).where('api_source', '==', service_id).select([]).stream()
            return sum(1 for _ in docs)
        except Exception:
            return 0

# ============================================================
# 수집 로그 기록
# ============================================================

def log_collection(api_source, api_name, collect_type,
                   total, fetched, inserted, updated, errors, error_msg, started_at):
    """수집 로그를 Firestore에 기록"""
    finished_at = datetime.now()
    duration = int((finished_at - started_at).total_seconds())
    try:
        fdb.collection('fss_collect_log').add({
            'api_source': api_source,
            'api_name': api_name,
            'collect_type': collect_type,
            'total_count': total,
            'fetched_count': fetched,
            'inserted_count': inserted,
            'updated_count': updated,
            'error_count': errors,
            'error_msg': error_msg or '',
            'started_at': started_at.isoformat(),
            'finished_at': finished_at.isoformat(),
            'duration_sec': duration,
        })
    except Exception as e:
        logger.error(f'로그 기록 실패: {e}')


def update_data_counts():
    """Firestore fss_config/data_counts 메타데이터 업데이트 (프론트엔드용)"""
    try:
        counts = {}
        totals = {}
        for col_name in ['fss_businesses', 'fss_products', 'fss_materials', 'fss_changes']:
            # 컬렉션 전체 건수: count() 집계 사용
            try:
                count_query = fdb.collection(col_name).count()
                results = count_query.get()
                totals[col_name] = results[0][0].value if results else 0
            except Exception:
                totals[col_name] = 0

            # API별 건수: 각 API에 대해 count() 집계
            for sid, info in ALL_APIS.items():
                if info['collection'] == col_name:
                    try:
                        q = fdb.collection(col_name).where('api_source', '==', sid).count()
                        r = q.get()
                        counts[sid] = r[0][0].value if r else 0
                    except Exception:
                        counts[sid] = counts.get(sid, 0)

        fdb.collection('fss_config').document('data_counts').set({
            'counts': counts,
            'total': totals,
            'updated_at': firestore.SERVER_TIMESTAMP,
        })
        logger.info(f'  📊 카운트 메타데이터 업데이트: {totals}')
    except Exception as e:
        logger.error(f'카운트 업데이트 실패: {e}')


# ============================================================
# 수집 메인 로직
# ============================================================

def collect_api(service_id, api_info, collect_type='incremental',
                chng_dt=None, resume=False):
    """단일 API 전체 수집"""
    global _quota_exceeded, _daily_write_count

    collection_name = api_info['collection']
    name = api_info['name']

    if _quota_exceeded:
        logger.info(f'⏭️ [{service_id}] {name} — 한도 초과로 건너뜀')
        return 'quota_exceeded'

    if not check_write_quota():
        logger.info(f'⏭️ [{service_id}] {name} — Firestore 쓰기 한도 도달')
        return 'write_limit'

    started_at = datetime.now()
    logger.info(f'▶ [{service_id}] {name} 수집 시작 ({collect_type})')

    # 1단계: 총 건수 확인
    dt_param = chng_dt if collect_type == 'incremental' and chng_dt else None
    total, _, status = fetch_api(service_id, 1, 1, dt_param)

    if status == 'quota_exceeded':
        logger.warning(f'  ⏭️ 한도 초과 — 이 API 건너뜀')
        log_collection(service_id, name, collect_type, 0, 0, 0, 0, 0,
                       'API 호출 한도 초과 (INFO-300)', started_at)
        return 'quota_exceeded'

    if total == 0:
        logger.info(f'  → 데이터 없음 (0건)')
        log_collection(service_id, name, collect_type, 0, 0, 0, 0, 0, None, started_at)
        return 'empty'

    # resume 모드: 이미 수집된 건수 확인
    start_from = 1
    if resume:
        already = get_collected_count(service_id, collection_name)
        if already >= total:
            logger.info(f'  ✅ 이미 완료: Firestore {already:,}건 / API {total:,}건')
            log_collection(service_id, name, collect_type + '_resume',
                           total, 0, 0, 0, 0, '이미 수집 완료', started_at)
            return 'already_done'
        elif already > 0:
            start_from = already + 1
            logger.info(f'  🔄 이어서 수집: Firestore {already:,}건 보유 → {start_from:,}번부터 시작 (총 {total:,}건)')
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

    try:
        batch = fdb.batch()
        batch_count = 0

        for start in range(start_from, total + 1, BATCH_SIZE):
            end = min(start + BATCH_SIZE - 1, total)
            _, rows, status = fetch_api(service_id, start, end, dt_param)

            if status == 'quota_exceeded':
                logger.warning(f'  ⚠️ {fetched:,}건까지 수집 후 API 한도 초과로 중단')
                if batch_count > 0:
                    batch.commit()
                error_msg = f'API 한도 초과 — {start_from}~{start-1}번 수집 완료'
                break

            if not rows:
                time.sleep(REQUEST_DELAY)
                continue

            # 업소 인허가 수집 시: 페이지 단위 신규 업소 감지
            new_ids = None
            if collection_name == 'fss_businesses':
                new_ids = detect_new_businesses(rows)
                if new_ids:
                    logger.info(f'    📋 이 페이지에서 신규 {len(new_ids)}건 감지')

            for row in rows:
                # Firestore 쓰기 한도 체크
                if not check_write_quota():
                    logger.warning(f'  ⚠️ Firestore 쓰기 한도 도달 ({_daily_write_count}건)')
                    if batch_count > 0:
                        batch.commit()
                    error_msg = f'Firestore 쓰기 한도 도달 — {fetched}건 수집 완료'
                    log_collection(service_id, name,
                                   collect_type + ('_resume' if resume else ''),
                                   total, fetched, inserted, updated, errors, error_msg, started_at)
                    return 'write_limit'

                try:
                    if collection_name == 'fss_businesses':
                        rc = upsert_business(batch, service_id, row, new_ids)
                    elif collection_name == 'fss_products':
                        rc = upsert_product(batch, service_id, row)
                    elif collection_name == 'fss_materials':
                        rc = upsert_material(batch, service_id, row)
                    elif collection_name == 'fss_changes':
                        rc = insert_change(batch, service_id, row)
                    else:
                        continue

                    if rc == 'quota_exceeded':
                        if batch_count > 0:
                            batch.commit()
                        error_msg = f'Firestore 쓰기 한도 — {fetched}건 수집 완료'
                        log_collection(service_id, name,
                                       collect_type + ('_resume' if resume else ''),
                                       total, fetched, inserted, updated, errors, error_msg, started_at)
                        return 'write_limit'

                    inserted += 1
                    fetched += 1
                    batch_count += 1

                except Exception as e:
                    errors += 1
                    if errors <= 5:
                        logger.warning(f'  Firestore 오류: {e} / row={row.get("LCNS_NO", "?")}')
                    if not error_msg:
                        error_msg = str(e)

            # 배치 커밋 (최대 499건)
            if batch_count >= 450:
                batch.commit()
                batch = fdb.batch()
                batch_count = 0

            # 진행률 로그
            total_fetched = (start_from - 1) + fetched if resume else fetched
            if fetched > 0 and fetched % 1000 < BATCH_SIZE:
                pct = (total_fetched / total * 100) if total else 0
                logger.info(f'  진행: {total_fetched:,}/{total:,} ({pct:.1f}%) 입력={inserted} (쓰기={_daily_write_count})')

            time.sleep(REQUEST_DELAY)

        # 남은 배치 커밋
        if batch_count > 0:
            batch.commit()

    except Exception as e:
        logger.error(f'  수집 중 오류: {e}')
        error_msg = str(e)

    elapsed = (datetime.now() - started_at).total_seconds()
    result_status = 'quota_exceeded' if _quota_exceeded else 'ok'

    if result_status == 'ok':
        logger.info(f'  ✅ 완료: {fetched:,}건 (입력={inserted}, 오류={errors}) [{elapsed:.0f}초] (일일 쓰기: {_daily_write_count})')
    else:
        logger.info(f'  ⏸️ 중단: {fetched:,}건 저장됨 [{elapsed:.0f}초]')

    log_collection(service_id, name,
                   collect_type + ('_resume' if resume else ''),
                   total, fetched, inserted, updated, errors, error_msg, started_at)

    return result_status


def collect_api_auto(service_id, api_info):
    """자동 모드: 미완료 API는 이어서 수집, 완료된 API는 증분 수집"""
    global _quota_exceeded

    if _quota_exceeded:
        logger.info(f'⏭️ [{service_id}] {api_info["name"]} — 한도 초과로 건너뜀')
        return 'quota_exceeded'

    if not check_write_quota():
        logger.info(f'⏭️ [{service_id}] {api_info["name"]} — Firestore 쓰기 한도 도달')
        return 'write_limit'

    collection_name = api_info['collection']
    name = api_info['name']

    # 1) API 총 건수 확인
    api_total, _, status = fetch_api(service_id, 1, 1, None)
    if status == 'quota_exceeded':
        return 'quota_exceeded'

    # 2) Firestore 건수 확인
    db_count = get_collected_count(service_id, collection_name)

    # 2-1) API 조회 실패 방어: api_total=0인데 Firestore에 데이터가 있으면 에러
    if api_total == 0 and status in ('error', 'empty'):
        if db_count > 0:
            logger.warning(f'⚠️ [{service_id}] {name}: API 조회 실패 (status={status}) '
                          f'but Firestore has {db_count:,}건 — 건너뛰기')
            return 'error'
        else:
            logger.info(f'  → [{service_id}] {name}: 데이터 없음 (API 및 Firestore 모두 0건)')
            return 'empty'

    # 3) 판단
    if api_total > 0 and db_count < api_total:
        pct = (db_count / api_total * 100) if api_total else 0
        logger.info(f'📊 [{service_id}] {name}: Firestore {db_count:,} / API {api_total:,} ({pct:.1f}%) → 이어서 수집')
        return collect_api(service_id, api_info,
                          collect_type='full', chng_dt=None, resume=True)
    else:
        week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y%m%d')
        logger.info(f'✅ [{service_id}] {name}: Firestore {db_count:,} / API {api_total:,} — 증분 수집 ({week_ago}~)')
        return collect_api(service_id, api_info,
                          collect_type='incremental', chng_dt=week_ago, resume=False)

# ============================================================
# 수집 현황
# ============================================================

def show_status():
    """현재 Firestore 수집 현황 출력"""
    print('\n' + '=' * 70)
    print('  식약처 데이터 수집 현황 (Firestore)')
    print('=' * 70)

    collections = [
        ('fss_businesses', '업소 인허가'),
        ('fss_products', '품목 제조'),
        ('fss_materials', '원재료'),
        ('fss_changes', '변경 이력'),
    ]
    print(f'\n{"컬렉션":<20} {"건수":>12}')
    print('-' * 35)
    for col, name in collections:
        try:
            count_query = fdb.collection(col).count()
            results = count_query.get()
            cnt = results[0][0].value if results else 0
            print(f'{name:<20} {cnt:>12,}')
        except Exception:
            try:
                docs = fdb.collection(col).select([]).stream()
                cnt = sum(1 for _ in docs)
                print(f'{name:<20} {cnt:>12,}')
            except Exception:
                print(f'{name:<20} {"(오류)":>12}')

    # API별 건수
    print(f'\n{"API":<10} {"이름":<25} {"상태":>8}')
    print('-' * 45)
    for sid, info in ALL_APIS.items():
        cnt = get_collected_count(sid, info['collection'])
        status = '✅' if cnt > 0 else '⬜'
        print(f'{sid:<10} {info["name"]:<25} {cnt:>8,} {status}')

    # 최근 수집 로그
    print(f'\n최근 수집 이력:')
    print('-' * 70)
    try:
        logs = fdb.collection('fss_collect_log').order_by(
            'started_at', direction=firestore.Query.DESCENDING
        ).limit(10).stream()

        for doc in logs:
            r = doc.to_dict()
            dt = (r.get('started_at', '') or '')[:16]
            err_info = f" ⚠️{r.get('error_msg', '')[:30]}" if r.get('error_msg') else ''
            print(f"  {dt} [{r.get('api_source', '')}] {r.get('api_name', '')} "
                  f"({r.get('collect_type', '')}) {r.get('fetched_count', 0):,}건 "
                  f"(+{r.get('inserted_count', 0)}/✗{r.get('error_count', 0)})"
                  f" {r.get('duration_sec', 0)}초{err_info}")
    except Exception:
        print('  (로그 없음)')

    print()

# ============================================================
# 설정 로드 (Firestore에서)
# ============================================================

def load_schedule_config():
    """Firestore에서 스케줄 설정 읽기"""
    try:
        doc = fdb.collection('fss_config').document('schedule').get()
        return doc.to_dict() if doc.exists else None
    except Exception:
        return None


def load_api_configs():
    """Firestore에서 API 설정 읽기"""
    try:
        docs = fdb.collection('fss_config').document('apis').collection('list').stream()
        rows = [doc.to_dict() for doc in docs]
        return rows if rows else None
    except Exception:
        return None

# ============================================================
# 메인
# ============================================================

def main():
    global _quota_exceeded, _daily_write_count

    parser = argparse.ArgumentParser(description='식약처 인허가 데이터 수집기 (Firestore)')
    parser.add_argument('--full', action='store_true', help='전체 수집 (최초 실행)')
    parser.add_argument('--resume', action='store_true', help='이어서 수집 (중단된 지점부터)')
    parser.add_argument('--auto', action='store_true', help='자동 모드 (미완료→이어서, 완료→증분) cron용')
    parser.add_argument('--status', action='store_true', help='수집 현황 확인')
    parser.add_argument('apis', nargs='*', help='특정 API만 수집 (예: I1220 I2829)')
    args = parser.parse_args()

    # Firestore 초기화
    init_firestore()

    try:
        if args.status:
            show_status()
            return

        # Firestore에서 설정 읽기
        db_schedule = load_schedule_config()
        db_api_configs = load_api_configs()

        # 설정 적용
        global API_KEY, BATCH_SIZE, REQUEST_DELAY
        if db_schedule:
            if db_schedule.get('api_key'):
                API_KEY = db_schedule['api_key']
            if db_schedule.get('batch_size'):
                BATCH_SIZE = int(db_schedule['batch_size'])
            if db_schedule.get('request_delay'):
                REQUEST_DELAY = float(db_schedule['request_delay'])
            logger.info(f'Firestore 설정 로드: batch={BATCH_SIZE}, delay={REQUEST_DELAY}s')

        # 수집 모드 결정
        if args.resume:
            collect_type = 'full'
        elif args.auto:
            collect_type = 'auto'
        else:
            collect_type = 'full' if args.full else (
                db_schedule.get('collect_mode', 'incremental') if db_schedule else 'incremental'
            )

        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
        chng_dt = yesterday if collect_type not in ('full', 'auto') else None

        # 수집 대상 결정
        if args.apis:
            targets = {k: v for k, v in ALL_APIS.items() if k in args.apis}
            if not targets:
                logger.error(f'유효하지 않은 API: {args.apis}')
                logger.info(f'사용 가능한 API: {list(ALL_APIS.keys())}')
                return
        elif db_api_configs:
            enabled_ids = [c['api_source'] for c in db_api_configs if c.get('is_enabled')]
            targets = {k: v for k, v in ALL_APIS.items() if k in enabled_ids}
            if not targets:
                logger.warning('설정에 활성화된 API가 없습니다. 전체 API로 진행합니다.')
                targets = ALL_APIS
            else:
                logger.info(f'Firestore 설정 기준: {len(targets)}개 API 활성')
        else:
            targets = ALL_APIS

        logger.info(f'{"="*60}')
        logger.info(f'식약처 데이터 수집 시작 ({collect_type}{"+ resume" if args.resume else ""}) [Firestore]')
        logger.info(f'대상: {len(targets)}개 API')
        logger.info(f'설정: batch_size={BATCH_SIZE}, delay={REQUEST_DELAY}s')
        logger.info(f'Firestore 쓰기 한도: {DAILY_WRITE_LIMIT:,}건/일')
        if chng_dt:
            logger.info(f'변경일자 기준: {chng_dt} 이후')
        logger.info(f'{"="*60}')

        total_start = time.time()
        _quota_exceeded = False
        _daily_write_count = 0

        # 수집 순서: 업소 → 품목 → 원재료 → 변경이력
        order = list(BUSINESS_APIS.keys()) + list(PRODUCT_APIS.keys()) + \
                list(MATERIAL_APIS.keys()) + list(CHANGE_APIS.keys())

        completed = []
        skipped = []

        for sid in order:
            if sid in targets:
                if collect_type == 'auto':
                    result = collect_api_auto(sid, targets[sid])
                else:
                    result = collect_api(sid, targets[sid], collect_type,
                                         chng_dt, resume=args.resume)
                if result in ('quota_exceeded', 'write_limit'):
                    skipped.append(sid)
                else:
                    completed.append(sid)

        elapsed = time.time() - total_start
        logger.info(f'{"="*60}')
        logger.info(f'수집 종료! 총 소요시간: {elapsed:.0f}초 ({elapsed/60:.1f}분)')
        logger.info(f'  완료: {len(completed)}개 API {completed}')
        logger.info(f'  Firestore 쓰기: {_daily_write_count:,}건')
        if skipped:
            logger.info(f'  ⏭️ 건너뜀: {len(skipped)}개 API {skipped}')
            logger.info(f'  → 내일 자동 수집 시 이어서 진행됩니다 (--auto)')
        logger.info(f'{"="*60}')

        # 프론트엔드용 카운트 메타데이터 업데이트
        if completed:
            update_data_counts()

        show_status()

    except Exception as e:
        logger.error(f'수집 중 오류: {e}')
        raise


if __name__ == '__main__':
    main()

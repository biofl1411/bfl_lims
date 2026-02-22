#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BioFoodLab 식약처 데이터 MariaDB → Firestore 1회성 마이그레이션

사용법:
  1. Firebase Console → 프로젝트 설정 → 서비스 계정 → 새 비공개 키 생성
  2. 키 파일을 이 스크립트와 같은 폴더에 serviceAccountKey.json 으로 저장
  3. pip install firebase-admin pymysql
  4. python3 migrate_to_firestore.py

  특정 테이블만: python3 migrate_to_firestore.py --table fss_businesses
  설정만:       python3 migrate_to_firestore.py --config-only
"""

import os
import sys
import json
import time
import argparse
from datetime import datetime

import pymysql
import firebase_admin
from firebase_admin import credentials, firestore

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
    'cursorclass': pymysql.cursors.DictCursor,
}

SERVICE_ACCOUNT_KEY = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'serviceAccountKey.json'
)

BATCH_LIMIT = 499  # Firestore batch write 한도 500, 여유 1

# ============================================================
# Firestore 초기화
# ============================================================

def init_firestore():
    if not os.path.exists(SERVICE_ACCOUNT_KEY):
        print(f'[오류] 서비스 계정 키 파일이 없습니다: {SERVICE_ACCOUNT_KEY}')
        print('Firebase Console → 프로젝트 설정 → 서비스 계정 → 새 비공개 키 생성')
        sys.exit(1)

    cred = credentials.Certificate(SERVICE_ACCOUNT_KEY)
    firebase_admin.initialize_app(cred)
    return firestore.client()

# ============================================================
# 마이그레이션 함수
# ============================================================

def migrate_businesses(conn, fdb):
    """fss_businesses → Firestore fss_businesses/{lcns_no}"""
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) as cnt FROM fss_businesses')
    total = cursor.fetchone()['cnt']
    print(f'\n[fss_businesses] 총 {total:,}건 이전 시작...')

    cursor.execute('SELECT * FROM fss_businesses')
    batch = fdb.batch()
    count = 0
    batch_count = 0

    for row in cursor:
        lcns_no = row.get('lcns_no', '')
        if not lcns_no:
            continue

        doc_ref = fdb.collection('fss_businesses').document(lcns_no)
        doc_data = {
            'api_source': row.get('api_source', ''),
            'lcns_no': lcns_no,
            'bssh_nm': row.get('bssh_nm', ''),
            'prsdnt_nm': row.get('prsdnt_nm') or '',
            'induty_nm': row.get('induty_nm') or '',
            'prms_dt': row.get('prms_dt') or '',
            'telno': row.get('telno') or '',
            'locp_addr': row.get('locp_addr') or '',
            'instt_nm': row.get('instt_nm') or '',
            'clsbiz_dvs_nm': row.get('clsbiz_dvs_nm') or '',
            'addr_sido': row.get('addr_sido') or '',
            'addr_sigungu': row.get('addr_sigungu') or '',
            'addr_dong': row.get('addr_dong') or '',
            'collected_at': str(row.get('collected_at', '')) if row.get('collected_at') else '',
        }
        batch.set(doc_ref, doc_data)
        count += 1
        batch_count += 1

        if batch_count >= BATCH_LIMIT:
            batch.commit()
            batch = fdb.batch()
            batch_count = 0
            if count % 5000 == 0:
                pct = count / total * 100 if total else 0
                print(f'  진행: {count:,}/{total:,} ({pct:.1f}%)')

    if batch_count > 0:
        batch.commit()

    print(f'  ✅ fss_businesses 완료: {count:,}건')
    cursor.close()
    return count


def migrate_products(conn, fdb):
    """fss_products → Firestore fss_products/{prdlst_report_no}"""
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) as cnt FROM fss_products')
    total = cursor.fetchone()['cnt']
    print(f'\n[fss_products] 총 {total:,}건 이전 시작...')

    cursor.execute('SELECT * FROM fss_products')
    batch = fdb.batch()
    count = 0
    batch_count = 0

    for row in cursor:
        report_no = row.get('prdlst_report_no', '')
        if not report_no:
            continue

        doc_ref = fdb.collection('fss_products').document(report_no)
        doc_data = {
            'api_source': row.get('api_source', ''),
            'lcns_no': row.get('lcns_no') or '',
            'bssh_nm': row.get('bssh_nm') or '',
            'prdlst_report_no': report_no,
            'prms_dt': row.get('prms_dt') or '',
            'prdlst_nm': row.get('prdlst_nm') or '',
            'prdlst_dcnm': row.get('prdlst_dcnm') or '',
            'production': row.get('production') or '',
            'hieng_lntrt_dvs_nm': row.get('hieng_lntrt_dvs_nm') or '',
            'child_crtfc_yn': row.get('child_crtfc_yn') or '',
            'pog_daycnt': row.get('pog_daycnt') or 0,
            'induty_cd_nm': row.get('induty_cd_nm') or '',
            'dispos': row.get('dispos') or '',
            'shap': row.get('shap') or '',
            'stdr_stnd': row.get('stdr_stnd') or '',
            'ntk_mthd': row.get('ntk_mthd') or '',
            'primary_fnclty': row.get('primary_fnclty') or '',
            'iftkn_atnt_matr_cn': row.get('iftkn_atnt_matr_cn') or '',
            'cstdy_mthd': row.get('cstdy_mthd') or '',
            'prdt_shap_cd_nm': row.get('prdt_shap_cd_nm') or '',
            'usage_info': row.get('usage_info') or '',
            'prpos': row.get('prpos') or '',
            'frmlc_mtrqlt': row.get('frmlc_mtrqlt') or '',
            'qlity_mntnc': row.get('qlity_mntnc') or '',
            'etqty_xport': row.get('etqty_xport') or '',
            'last_updt_dtm': row.get('last_updt_dtm') or '',
            'collected_at': str(row.get('collected_at', '')) if row.get('collected_at') else '',
        }
        batch.set(doc_ref, doc_data)
        count += 1
        batch_count += 1

        if batch_count >= BATCH_LIMIT:
            batch.commit()
            batch = fdb.batch()
            batch_count = 0
            if count % 5000 == 0:
                pct = count / total * 100 if total else 0
                print(f'  진행: {count:,}/{total:,} ({pct:.1f}%)')

    if batch_count > 0:
        batch.commit()

    print(f'  ✅ fss_products 완료: {count:,}건')
    cursor.close()
    return count


def migrate_materials(conn, fdb):
    """fss_materials → Firestore fss_materials/{report_no}_{ordno}"""
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) as cnt FROM fss_materials')
    total = cursor.fetchone()['cnt']
    print(f'\n[fss_materials] 총 {total:,}건 이전 시작...')

    cursor.execute('SELECT * FROM fss_materials')
    batch = fdb.batch()
    count = 0
    batch_count = 0

    for row in cursor:
        report_no = row.get('prdlst_report_no', '')
        ordno = str(row.get('rawmtrl_ordno', '0'))
        if not report_no:
            continue

        doc_id = f'{report_no}_{ordno}'
        doc_ref = fdb.collection('fss_materials').document(doc_id)
        doc_data = {
            'api_source': row.get('api_source', ''),
            'lcns_no': row.get('lcns_no') or '',
            'bssh_nm': row.get('bssh_nm') or '',
            'prdlst_report_no': report_no,
            'prms_dt': row.get('prms_dt') or '',
            'prdlst_nm': row.get('prdlst_nm') or '',
            'prdlst_dcnm': row.get('prdlst_dcnm') or '',
            'rawmtrl_nm': row.get('rawmtrl_nm') or '',
            'rawmtrl_ordno': ordno,
            'chng_dt': row.get('chng_dt') or '',
            'etqty_xport': row.get('etqty_xport') or '',
            'collected_at': str(row.get('collected_at', '')) if row.get('collected_at') else '',
        }
        batch.set(doc_ref, doc_data)
        count += 1
        batch_count += 1

        if batch_count >= BATCH_LIMIT:
            batch.commit()
            batch = fdb.batch()
            batch_count = 0
            if count % 5000 == 0:
                pct = count / total * 100 if total else 0
                print(f'  진행: {count:,}/{total:,} ({pct:.1f}%)')

    if batch_count > 0:
        batch.commit()

    print(f'  ✅ fss_materials 완료: {count:,}건')
    cursor.close()
    return count


def migrate_changes(conn, fdb):
    """fss_changes → Firestore fss_changes/{auto_id}"""
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) as cnt FROM fss_changes')
    total = cursor.fetchone()['cnt']
    print(f'\n[fss_changes] 총 {total:,}건 이전 시작...')

    cursor.execute('SELECT * FROM fss_changes')
    batch = fdb.batch()
    count = 0
    batch_count = 0

    for row in cursor:
        doc_ref = fdb.collection('fss_changes').document()
        doc_data = {
            'api_source': row.get('api_source', ''),
            'lcns_no': row.get('lcns_no') or '',
            'bssh_nm': row.get('bssh_nm') or '',
            'induty_cd_nm': row.get('induty_cd_nm') or '',
            'telno': row.get('telno') or '',
            'site_addr': row.get('site_addr') or '',
            'chng_dt': row.get('chng_dt') or '',
            'chng_bf_cn': row.get('chng_bf_cn') or '',
            'chng_af_cn': row.get('chng_af_cn') or '',
            'chng_prvns': row.get('chng_prvns') or '',
            'collected_at': str(row.get('collected_at', '')) if row.get('collected_at') else '',
        }
        batch.set(doc_ref, doc_data)
        count += 1
        batch_count += 1

        if batch_count >= BATCH_LIMIT:
            batch.commit()
            batch = fdb.batch()
            batch_count = 0
            if count % 5000 == 0:
                pct = count / total * 100 if total else 0
                print(f'  진행: {count:,}/{total:,} ({pct:.1f}%)')

    if batch_count > 0:
        batch.commit()

    print(f'  ✅ fss_changes 완료: {count:,}건')
    cursor.close()
    return count


def migrate_collect_log(conn, fdb):
    """fss_collect_log → Firestore fss_collect_log/{auto_id}"""
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) as cnt FROM fss_collect_log')
    total = cursor.fetchone()['cnt']
    print(f'\n[fss_collect_log] 총 {total:,}건 이전 시작...')

    cursor.execute('SELECT * FROM fss_collect_log ORDER BY started_at')
    batch = fdb.batch()
    count = 0
    batch_count = 0

    for row in cursor:
        doc_ref = fdb.collection('fss_collect_log').document()
        doc_data = {
            'api_source': row.get('api_source', ''),
            'api_name': row.get('api_name') or '',
            'collect_type': row.get('collect_type') or '',
            'total_count': row.get('total_count') or 0,
            'fetched_count': row.get('fetched_count') or 0,
            'inserted_count': row.get('inserted_count') or 0,
            'updated_count': row.get('updated_count') or 0,
            'error_count': row.get('error_count') or 0,
            'error_msg': row.get('error_msg') or '',
            'started_at': str(row.get('started_at', '')) if row.get('started_at') else '',
            'finished_at': str(row.get('finished_at', '')) if row.get('finished_at') else '',
            'duration_sec': row.get('duration_sec') or 0,
        }
        batch.set(doc_ref, doc_data)
        count += 1
        batch_count += 1

        if batch_count >= BATCH_LIMIT:
            batch.commit()
            batch = fdb.batch()
            batch_count = 0

    if batch_count > 0:
        batch.commit()

    print(f'  ✅ fss_collect_log 완료: {count:,}건')
    cursor.close()
    return count


def migrate_config(conn, fdb):
    """fss_schedule_config + fss_api_config → Firestore fss_config/"""
    cursor = conn.cursor()

    # 스케줄 설정
    try:
        cursor.execute('SELECT * FROM fss_schedule_config WHERE id=1')
        row = cursor.fetchone()
        if row:
            fdb.collection('fss_config').document('schedule').set({
                'collect_hour': row.get('collect_hour', 3),
                'collect_minute': row.get('collect_minute', 0),
                'collect_mode': row.get('collect_mode', 'incremental'),
                'is_active': bool(row.get('is_active', 1)),
                'api_key': row.get('api_key', ''),
                'batch_size': row.get('batch_size', 100),
                'request_delay': float(row.get('request_delay', 0.3)),
            })
            print('  ✅ fss_config/schedule 저장 완료')
        else:
            # 기본값 저장
            fdb.collection('fss_config').document('schedule').set({
                'collect_hour': 3,
                'collect_minute': 0,
                'collect_mode': 'incremental',
                'is_active': True,
                'api_key': 'e5a1d9f07d6c4424a757',
                'batch_size': 100,
                'request_delay': 0.3,
            })
            print('  ✅ fss_config/schedule 기본값 저장')
    except Exception as e:
        print(f'  ⚠️ schedule 설정 이전 실패: {e}')

    # API 설정
    try:
        cursor.execute('SELECT * FROM fss_api_config')
        rows = cursor.fetchall()
        count = 0
        for row in rows:
            api_source = row.get('api_source', '')
            if not api_source:
                continue
            doc_data = {
                'api_source': api_source,
                'api_name': row.get('api_name') or '',
                'category': row.get('category') or '',
                'is_enabled': bool(row.get('is_enabled', 1)),
                'enabled_fields': row.get('enabled_fields') or '[]',
                'all_fields': row.get('all_fields') or '[]',
            }
            fdb.collection('fss_config').document('apis').collection('list').document(api_source).set(doc_data)
            count += 1
        print(f'  ✅ fss_config/apis 저장 완료: {count}개 API')
    except Exception as e:
        print(f'  ⚠️ API 설정 이전 실패: {e}')

    cursor.close()


# ============================================================
# 메인
# ============================================================

def main():
    parser = argparse.ArgumentParser(description='식약처 데이터 MariaDB → Firestore 마이그레이션')
    parser.add_argument('--table', help='특정 테이블만 이전 (fss_businesses, fss_products, fss_materials, fss_changes)')
    parser.add_argument('--config-only', action='store_true', help='설정(schedule/api)만 이전')
    args = parser.parse_args()

    print('=' * 60)
    print('  식약처 데이터 MariaDB → Firestore 마이그레이션')
    print('=' * 60)

    # Firestore 초기화
    fdb = init_firestore()
    print('[Firestore] 연결 성공')

    # MariaDB 연결
    try:
        conn = pymysql.connect(**DB_CONFIG)
        print(f'[MariaDB] 연결 성공: {DB_CONFIG["host"]}:{DB_CONFIG["port"]}/{DB_CONFIG["database"]}')
    except pymysql.Error as e:
        print(f'[오류] MariaDB 연결 실패: {e}')
        sys.exit(1)

    start_time = time.time()
    total_migrated = 0

    try:
        if args.config_only:
            migrate_config(conn, fdb)
            return

        tables = {
            'fss_businesses': migrate_businesses,
            'fss_products': migrate_products,
            'fss_materials': migrate_materials,
            'fss_changes': migrate_changes,
        }

        if args.table:
            if args.table not in tables:
                print(f'[오류] 유효하지 않은 테이블: {args.table}')
                print(f'사용 가능: {list(tables.keys())}')
                return
            total_migrated += tables[args.table](conn, fdb)
        else:
            for name, func in tables.items():
                total_migrated += func(conn, fdb)

            # 수집 로그 이전
            total_migrated += migrate_collect_log(conn, fdb)

            # 설정 이전
            migrate_config(conn, fdb)

    finally:
        conn.close()

    elapsed = time.time() - start_time
    print(f'\n{"=" * 60}')
    print(f'  마이그레이션 완료!')
    print(f'  총 이전: {total_migrated:,}건')
    print(f'  소요 시간: {elapsed:.0f}초 ({elapsed/60:.1f}분)')
    print(f'{"=" * 60}')


if __name__ == '__main__':
    main()

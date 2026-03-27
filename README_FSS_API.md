# 제조가공업소 API (식약처 공공 데이터)

> 메인 문서: [README.md](README.md)

---

## 1. 식약처 공공 API 개요 (식품안전나라 OpenAPI)

| 항목 | 내용 |
|------|------|
| **API 키** | `e5a1d9f07d6c4424a757` |
| **Base URL** | `https://openapi.foodsafetykorea.go.kr/api` |
| **호출 형식** | `{BASE_URL}/{API_KEY}/{서비스ID}/json/{시작}/{끝}` |
| **수집기** | `collector.py` (Firestore 직접 저장) |
| **서비스 수** | 16개 (업소 9 + 품목 2 + 원재료 3 + 변경이력 2) |
| **사용 페이지** | `salesMgmt.html` (업체찾기), `admin_collect_status.html` |

---

## 2. Backend API (`api_server.py`)

Flask REST API 서버 (port 5003)

| 엔드포인트 | 메서드 | 설명 |
|-----------|--------|------|
| `/api/businesses` | GET | 업소 검색 (지역 드릴다운 + 키워드) |
| `/api/region/stats` | GET | 지역별 업소 수 통계 (3레벨) |
| `/api/products` | GET | 제품 검색 |
| `/api/materials` | GET | 원재료 검색 |
| `/api/changes` | GET | 인허가 변경 이력 |
| `/api/status` | GET | 수집 현황 (테이블별 건수) |
| `/api/collect/detail` | GET | API별 수집 상세 현황 |
| `/api/industries` | GET | 업종 목록 (필터용) |
| `/api/admin/settings` | GET/POST | 수집 설정 조회/저장 |
| `/api/admin/collect` | POST | 수동 수집 트리거 |

---

## 3. 데이터 수집기 (`collector.py`)

- 매일 새벽 3시 KST 자동 실행 (cron)
- 식약처 공공 API 16개에서 전국 데이터 수집 → MariaDB 저장
- 모드: 증분(incremental) / 전체(full) / 이어서(resume) / 자동(auto)

---

## 4. 식약처 API → Firestore 마이그레이션

MariaDB에서 Firestore로 식약처 공공 API 데이터 전체 이관 완료 (2026-02-22).

| 항목 | 내용 |
|------|------|
| **마이그레이션 스크립트** | `migrate_to_firestore.py` (1회성, MariaDB → Firestore) |
| **자동 수집기** | `collector.py` (Firestore 직접 저장, systemd timer) |
| **서비스 계정 키** | `serviceAccountKey.json` (서버 `~/bfl_lims/`) |
| **Firestore 무료 쓰기 한도** | 일 18,000건 (20,000 중 여유 2,000) |

### 수집 API 목록 (16개)

| 구분 | API 코드 | 이름 | Firestore 컬렉션 |
|------|----------|------|------------------|
| 업소 | I1220 | 식품제조가공업 | `fss_businesses` |
| 업소 | I2829 | 즉석판매제조가공업 | `fss_businesses` |
| 업소 | I-0020 | 건강기능식품 전문/벤처제조업 | `fss_businesses` |
| 업소 | I1300 | 축산물 가공업 | `fss_businesses` |
| 업소 | I1320 | 축산물 식육포장처리업 | `fss_businesses` |
| 업소 | I2835 | 식육즉석판매가공업 | `fss_businesses` |
| 업소 | I2831 | 식품소분업 | `fss_businesses` |
| 업소 | C001 | 수입식품등영업신고 | `fss_businesses` |
| 업소 | I1260 | 식품등수입판매업 | `fss_businesses` |
| 품목 | I1250 | 식품(첨가물)품목제조보고 | `fss_products` |
| 품목 | I1310 | 축산물 품목제조정보 | `fss_products` |
| 원재료 | C002 | 식품(첨가물) 원재료 | `fss_materials` |
| 원재료 | C003 | 건강기능식품 원재료 | `fss_materials` |
| 원재료 | C006 | 축산물 원재료 | `fss_materials` |
| 변경 | I2859 | 식품업소 인허가 변경 정보 | `fss_changes` |
| 변경 | I2860 | 건강기능식품업소 인허가 변경 정보 | `fss_changes` |

---

## 5. Firestore 컬렉션 (FSS 관련)

| 컬렉션 경로 | 설명 | 비고 |
|-------------|------|------|
| `fss_businesses/{lcns_no}` | 식약처 업소 데이터 (~11,200건) | 인허가번호 키 |
| `fss_products/{auto_id}` | 식약처 품목 데이터 (~661,000건) | 자동 ID |
| `fss_changes/{auto_id}` | 식약처 인허가 변경이력 | 자동 ID |
| `fss_materials/{auto_id}` | 식약처 원재료 | 자동 ID |
| `fss_collection_log/{auto_id}` | API 수집 로그 (날짜/건수/오류) | 자동 ID |

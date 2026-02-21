# BioFoodLab LIMS

식품 시험 검사 기관을 위한 **통합 웹 기반 실험실 정보 관리 시스템** (Laboratory Information Management System)

**배포 (서버)**: https://14.7.14.31:8443/
**배포 (GitHub Pages)**: https://biofl1411.github.io/bfl_lims/

---

## 기술 스택

| 구분 | 기술 |
|------|------|
| Frontend | Vanilla HTML/CSS/JS, Tailwind CSS (CDN), Chart.js, Leaflet.js |
| Backend | Flask (Python), MariaDB 8.0 |
| Database | **Firebase Firestore** (클라우드 NoSQL), localStorage (보조) |
| Storage | **Firebase Storage** (파일 업로드) |
| 외부 API | VWORLD (지도 타일), Kakao Maps (주소검색/길찾기), 식약처 공공 API (16개) |
| 폰트 | Pretendard, Outfit (Google Fonts) |
| 배포 | GitHub Pages (정적 프론트엔드), bioflsever (Flask API) |

---

## 프로젝트 구조

```
bfl_lims/
├── index.html                      # 대시보드 (메인)
├── companyRegForm_v2.html          # ★ 영업관리 > 고객사 신규등록 (OCR + 사용자관리 연동)
├── companyMgmt.html                # 영업관리 > 고객사 관리 목록
├── inspectionMgmt.html             # 접수관리 > 검사목적관리
├── sampleReceipt.html              # 접수관리 > 접수 등록 (API 연동)
├── itemAssign.html                 # 시험결재 > 항목배정
├── userMgmt.html                   # 관리자 > 사용자관리
├── salesMgmt.html                  # 영업관리 (지도 + 고객사)
├── adminSettings.html              # 관리자 > 기타 설정 (등급규칙/신호등/공휴일)
├── admin_api_settings.html          # 관리자 > API 수집 설정
├── admin_collect_status.html        # 관리자 > 수집 현황
├── receipt_api_final.py             # 시료접수 API 서버 (Flask, port 5001)
├── ocr_proxy.py                     # OCR 프록시 서버 (Flask, HTTPS port 5002)
├── SETUP_GUIDE.md                   # API 서버 실행 가이드
├── data/
│   ├── sido.json                    # 시도 경계 GeoJSON
│   ├── sigungu.json                 # 시군구 경계 GeoJSON
│   └── dong.json                    # 읍면동 경계 GeoJSON
├── js/
│   ├── sidebar.js                   # ★ 통합 사이드바 (Single Source of Truth) — 전체 메뉴 정의·렌더링·CSS
│   ├── firebase-init.js             # ★ Firebase 초기화 + Firestore/Storage 전역 변수 + firebase-ready 이벤트
│   ├── food_item_fee_mapping.js     # 수수료 매핑 데이터 (9,237건, 16개 검사목적, purpose 태그)
│   └── ref_nonstandard_data.js      # 참고용(기준규격외) 데이터 (3,374건)
├── img/
│   └── bfl_logo.svg                 # BFL 로고
├── api_server.py                    # Flask REST API 서버 (식약처 데이터, port 5060)
├── collector.py                     # 식약처 데이터 수집기 (cron)
└── deploy.ps1                       # 배포 스크립트
```

---

## 메뉴 구조 및 구현 현황

사이드바 메뉴: **11개 그룹, 38개 서브메뉴** (활성 21개 + 비활성 17개)

| # | 메뉴 | 서브메뉴 수 | 상태 | 구현 파일 |
|---|------|------------|------|-----------|
| 1 | 대시보드 | — | 구현됨 | `index.html` |
| 2 | 영업 관리 | 12개 | 부분 구현 | `salesMgmt.html` |
| 3 | 접수 관리 | 7개 | 부분 구현 | `inspectionMgmt.html`, `sampleReceipt.html` |
| 4 | 시험 결재 | 9개 | 부분 구현 | `itemAssign.html` |
| 5 | 성적 관리 | — | 미구현 | — |
| 6 | 재무 관리 | — | 미구현 | — |
| 7 | 통계 분석 | — | 미구현 | — |
| 8 | 문서 관리 | — | 미구현 | — |
| 9 | 재고/시약 관리 | — | 미구현 | — |
| 10 | 공지 | — | 미구현 | — |
| 11 | 관리자 | 10개 | 부분 구현 | `userMgmt.html`, `adminSettings.html`, `admin_api_settings.html`, `admin_collect_status.html` |

### 관리자 서브메뉴 (10개)
| 서브메뉴 | 상태 | 파일 |
|----------|------|------|
| 사용자 관리 | 구현됨 | `userMgmt.html` |
| 부서 관리 | 미구현 | — |
| 팀 관리 | 미구현 | — |
| 권한 설정 | 미구현 | — |
| 기타 설정 | 구현됨 | `adminSettings.html` |
| 대시보드 권한 | 미구현 | — |
| 알림 설정 | 미구현 | — |
| 시스템 로그 | 미구현 | — |
| API 수집 설정 | 구현됨 | `admin_api_settings.html` |
| 수집 현황 | 구현됨 | `admin_collect_status.html` |

---

## 주요 기능

### 대시보드 (`index.html`)
- KPI 카드 4개 (매출/접수/검사/재고)
- 월별 매출 추이 차트
- 최근 접수 현황 테이블, 검사 진행률, 공지사항

### 영업관리 (`salesMgmt.html`)
- **지도 3단계 드릴다운**: 시도 → 시군구 → 읍면동 (Leaflet + VWORLD 타일)
- **식약처 업소 검색**: 13만+ 업소 DB, 업종별 필터, 페이지네이션
- **카카오맵 연동**: 주소검색, 길찾기
- **12개 서브메뉴**: 고객사관리, 업무일지, 차량일지, 미수금, 거래명세표, 계산서발행, 업체조회, 긴급협조, 세금계산서미발행, 영업통계, 영업설정, API설정
- **신규 등록 버튼**: `companyRegForm_v2.html`로 이동

### 고객사 신규등록 (`companyRegForm_v2.html`)

salesMgmt.html 고객사관리 > "+ 신규 등록" 버튼 클릭 시 이동하는 독립 페이지.

- **7개 섹션**: 기본정보, 주소, 인허가정보, 고객사담당자, 세금계산서담당자, 메모/비고, 변경이력
- **OCR 자동입력**: 사업자등록증 OCR + 인허가문서 OCR (`ocr_proxy.py` 연동, CLOVA OCR)
- **업체명 모달 선택**: 등록된 업체 목록에서 선택 또는 직접 입력 (담당자 카드 + 세금계산서 담당자)
- **자사 담당자 연동**: `userMgmt.html`의 USERS_DATA(56명) + localStorage 병합
  - 부서 드롭다운: 영업 관련 4개만 표시 (고객지원팀, 마케팅사업부, 고객관리, 지사)
  - 접수자 드롭다운: 사용자관리의 "접수자" 필드 고유값 표시 (15개)
- **담당자 카드**: 동적 추가/삭제, 중복 확인, 이메일 필수값(*)
- **세금계산서 담당자**: 1번 담당자 정보 복사 기능, 업체명 모달 선택
- **거래처 등급**: 관리자 설정 등급규칙 기반 자동 산출
- **우편번호 검색**: 카카오 주소 API 연동
- **사업자등록증 영문 정보**: 아코디언 토글 (영문 회사명/주소/업태/종목)

### OCR 프록시 (`ocr_proxy.py`)

Flask HTTPS 서버 (port 5002) — CLOVA OCR API 프록시

| 엔드포인트 | 메서드 | 설명 |
|-----------|--------|------|
| `/api/ocr/business-registration` | POST | 사업자등록증 OCR 인식 |
| `/api/ocr/license` | POST | 인허가문서 OCR 인식 |
| `/api/ocr/health` | GET | 서버 상태 확인 |

### 검사관리 (`inspectionMgmt.html`)
- **6탭 구조**: 검사분야, 검사목적, 식품유형, 검사항목, 항목그룹, 수수료
- **데이터 저장**: Firebase Firestore 영구 저장 (6탭 모두)
- **검사목적 탭**: 카드 목록 + 상세 패널, 접수번호 세그먼트 구성, 선택 삭제 기능
- **접수번호 세그먼트 시스템**: 구분 수(1~8), 구분자(하이픈/없음), 7가지 타입 지원
  - 타입: 고정문자(`fixed`), 분야코드(`field`), 년도(`year`), 월(`month`), 일(`day`), 일련번호(`serial`), 목적번호(`purpose`)
  - 세그먼트 설정 Firestore 영구 저장/복원 (`P[].segments`, `P[].segSep`, `P[].segCnt`)
  - 각 구분별 ℹ️ 설명 텍스트 표시
  - 월/일: 1~12월/1~31일 셀렉트 드롭다운 (기본값: 현재 월/일)
  - 일련번호 초기화 설명: 세그먼트 구성에 맞게 동적 표시
- **식품유형 탭**: 카드뷰 + 아코디언뷰, 검체유형별 카드 분리
- **인라인 데이터**: FULL_FOOD_TYPES (894카드, 3,062항목)
- **외부 JS**: `food_item_fee_mapping.js` (9,237건, 16개 검사목적, purpose 태그 포함), `ref_nonstandard_data.js` (참고용(기준규격외) 3,374건)
- **시료명 경계 기반 그룹핑**: 시료명별 항목 세트 수집 → 동일 세트를 카드로 묶는 정확한 추출 방식
- **MANAGER_MAP**: itemAssign.html 실제 데이터에서 항목담당자 로드 (92개 매핑, 하드코딩 제거)
- **findManager() 폴백**: 검체유형||항목명 정확 매치 → 항목명만으로 매치
- **실시간 담당자 업데이트**: 상세패널에서 항목명 변경 시 MANAGER_MAP 기반 담당자 자동 갱신
- **상세 패널**: 항목 수정, 라벨 태그 관리, 좌우 항목 이동 (◀ ▶), 제목에 검체유형 표시
- **카드 기능**: 선택 삭제, 8가지 정렬 (기본/항목명/검체유형/담당자/수수료↑↓/항목수↑↓)
- **변경 감지**: 필드 변경 시 민트색(#00bfa5) "변경사항 있음" 표시 + 저장 버튼 강조 + 패널 테두리

### 시료접수 (`sampleReceipt.html`)
- **API 연동**: `receipt_api_final.py` (Flask, port 5001)와 연동
- **폴백 모드**: API 서버 미실행 시에도 내장 폴백 데이터로 동작
- **서버 상태 표시**: 헤더에 연결 상태 인디케이터 (🟢 연결됨 / 🔴 오프라인)
- **6개 아코디언 섹션**: 접수 기본정보, 업체정보, 시료정보, 검사정보, 의뢰인 정보, 팀별 메모
- **API 연동 기능**: 검사목적 로드, 검체유형 검색, 접수번호 할당(스레드 안전), 업체 검색
- **팀별 메모 권한**: 현재 로그인 팀만 편집, 나머지 읽기 전용
- **임시저장/불러오기**: localStorage 기반

### 시료접수 API (`receipt_api_final.py`)

Flask REST API 서버 (port 5001) — `food_item_fee_mapping.js` 데이터 기반

| 엔드포인트 | 메서드 | 설명 |
|-----------|--------|------|
| `/api/health` | GET | 서버 상태 확인 |
| `/api/test-purposes` | GET | 검사목적 조회 (`?field=식품\|축산`) |
| `/api/food-types` | GET | 검체유형 조회 (`?field=&purpose=`) |
| `/api/receipt-no/allocate` | POST | 접수번호 할당 (스레드 안전) |
| `/api/companies/search` | GET | 업체 검색 (`?q=`) |
| `/api/items/search` | GET | 검사항목 검색 (`?q=&purpose=`) |

### 항목배정 (`itemAssign.html`)
- 담당자 26명 배정 현황 테이블 (이름/부서/파트/직급/배정항목수/진행완료지연/업무부하율)

### 사용자관리 (`userMgmt.html`)
- **56명 사용자 목록**, 통계 카드 4개 (전체/부서수/직급수/재직자)
- **테이블 컬럼**: No, 아이디, 부서, 팀, 직급, 입사일, 퇴사일, 관리
- **검색/필터**: 아이디·이름 검색, 부서별(9개)/직급별(8개) 필터
- **인라인 편집**: 수정 버튼 클릭 → 해당 행이 input 필드로 전환 (부서/팀/직급/입사일/퇴사일)
- **헤더 정렬**: 컬럼 헤더 클릭으로 오름차순/내림차순 토글 (한국어 정렬 `localeCompare('ko')`)
- **정렬 상태 유지**: 수정 후에도 정렬 상태 유지, 재설정 버튼으로 초기화
- **엑셀 내보내기**: CSV UTF-8 BOM 다운로드 (`사용자목록_YYYY-MM-DD.csv`)
- **비밀번호 초기화**: PW초기화 버튼 (초기 비밀번호: `bfl1234`)
- **사용자 추가**: 모달 팝업으로 새 사용자 등록

### 관리자 설정 (`adminSettings.html`)

3개 탭으로 구성: **신호등 규칙**, **등급 규칙**, **공휴일/달력 관리**

**① 신호등 규칙** — 고객사 미수금 경과일 기반 5단계 신호 분류

| 신호등 | 색상 | 미수금 경과일 (기본값) |
|--------|------|---------------------|
| 🟢 정상 | 초록 | 0~30일 |
| 🔵 양호 | 파랑 | 31~60일 |
| 🟡 주의 | 노랑 | 61~90일 |
| 🟠 경고 | 주황 | 91~120일 |
| 🔴 위험 | 빨강 | 121일 이상 |

- 저장소: `localStorage.bfl_signal_rules`
- 경과일 범위 직접 수정 가능

**② 등급 규칙** — 복합 점수 방식 (5개 항목 총 100점)

| # | 항목 | 배점 | 기준 |
|---|------|------|------|
| 1 | 연간 매출액 | 40점 | 5단계 (1000만/3000만/5000만/1억 기준) |
| 2 | 거래 빈도 | 25점 | 5단계 (월 1건/3건/5건/10건 기준) |
| 3 | 거래 기간 | 15점 | 5단계 (1년/2년/3년/5년 기준) |
| 4 | 결제 신뢰도 | 15점 | 신호등 규칙 자동 연동 (🟢15점~🔴3점) |
| 5 | 계약 형태 | 5점 | 3단계 (단발성/반복거래/정기계약, 조건 텍스트 편집 가능) |

- 등급 산출: VIP(90점↑), A(70점↑), B(50점↑), C(49점↓)
- 저장소: `localStorage.bfl_grade_rules`
- 결제 신뢰도 ↔ 신호등 규칙 실시간 연동 (`updatePaymentSignalDisplay()`)
- 계약 형태 조건명: 자유 텍스트 입력으로 수정 가능

**③ 공휴일/달력 관리**

- 수동 입력: 날짜 + 명칭으로 휴일 추가
- 일괄 등록: 2026년 공휴일 13개 자동 추가
- 저장소: `localStorage.bfl_holiday_data` (상세), `localStorage.bfl_holidays` (날짜 배열)
- sampleReceipt.html 워킹데이 계산에 활용

### 관리자 - API 수집 (`admin_api_settings.html`, `admin_collect_status.html`)
- 식약처 공공 API 16개 활성화/설정
- 수집 현황 모니터링

---

## Backend API (`api_server.py`)

Flask REST API 서버 (port 5060)

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

### 데이터 수집기 (`collector.py`)
- 매일 새벽 3시 KST 자동 실행 (cron)
- 식약처 공공 API 16개에서 전국 데이터 수집 → MariaDB 저장
- 모드: 증분(incremental) / 전체(full) / 이어서(resume) / 자동(auto)

---

## 데이터 저장소

### Firebase Firestore (주 저장소)

Firebase 프로젝트: `bfl-lims` / SDK: Firebase compat v10.14.1

| Firestore 경로 | 용도 | 사용 페이지 | 저장 방식 |
|---------------|------|------------|----------|
| `settings/inspectionPurposes` | 검사목적 배열 (P) — 접수번호 세그먼트 포함 | `inspectionMgmt.html` | 단일 문서 |
| `settings/inspectionFields` | 검사분야 배열 (FIELDS) | `inspectionMgmt.html` | 단일 문서 |
| `settings/adminSettings` | 신호등/등급/공휴일 규칙 | `adminSettings.html` | 단일 문서 |
| `users/{docId}` | 사용자 관리 데이터 (56명) | `userMgmt.html` | 컬렉션 |
| `companies/{docId}` | 고객사 등록 데이터 | `companyRegForm_v2.html`, `companyMgmt.html` | 컬렉션 |
| `foodTypes/{docId}` | 식품유형 데이터 (894카드) | `inspectionMgmt.html` | 컬렉션 (배치) |
| `itemGroups/{docId}` | 항목그룹 데이터 (5,695건) | `inspectionMgmt.html` | 컬렉션 (배치) |
| `inspectionFees/{docId}` | 수수료 데이터 (7,481건) | `inspectionMgmt.html` | 컬렉션 (배치) |

> **대용량 데이터**: Firestore 단일 문서 1MB 제한으로 인해 식품유형·항목그룹·수수료는 **컬렉션 배치 방식**으로 저장 (500건씩 batch.set())

### Firebase Storage (파일 저장소)

| 경로 | 용도 | 사용 페이지 |
|------|------|------------|
| `companies/{companyId}/` | 고객사 첨부 파일 (사업자등록증, 인허가문서 등) | `companyRegForm_v2.html` |

### localStorage (보조 저장소 — 레거시)

| 키 | 용도 | 사용 페이지 |
|----|------|------------|
| `bfl_signal_rules` | 신호등 규칙 (미수금 경과일 5단계) — Firestore 전환 완료 | `adminSettings.html` |
| `bfl_grade_rules` | 등급 규칙 (복합 점수 5개 항목) — Firestore 전환 완료 | `adminSettings.html` |
| `bfl_holiday_data` | 공휴일 상세 — Firestore 전환 완료 | `adminSettings.html` |
| `bfl_holidays` | 공휴일 날짜 배열 | `sampleReceipt.html` |
| `bfl_users_data` | 사용자 관리 — Firestore 전환 완료 | `userMgmt.html` |

---

## 디자인 시스템

| 요소 | 값 |
|------|-----|
| Primary | `#1a73e8` |
| Success | `#43a047` |
| Warning | `#fb8c00` |
| Danger | `#e53935` |
| Background | `#f8f9fa` |
| Sidebar | `#1a2332` (dark navy) |
| Font | `Pretendard`, `-apple-system`, `sans-serif` |
| Body 크기 | 14px |
| Title 크기 | 16px |
| Sidebar 너비 | 250px (고정) |
| Layout | 사이드바 + 유동 메인 콘텐츠 (100vh) |

---

## 서버 환경

| 항목 | 값 |
|------|-----|
| Host | bioflsever (Ubuntu 24.04) |
| 공인 IP | 14.7.14.31 |
| 내부 IP | 192.168.0.96 |
| SSH | port 2222 |
| DB | MariaDB 8.0, database: `fss_data` |
| 웹서버 | nginx → HTTPS 8443 (LIMS 프론트엔드 + API 리버스 프록시) |
| API (시료접수) | http://127.0.0.1:5001 → nginx `/api/*` (`receipt_api_final.py`) |
| API (OCR프록시) | http://127.0.0.1:5002 → nginx `/ocr/*` (`ocr_proxy.py`) |
| API (식약처) | http://127.0.0.1:5050 → nginx `/fss/*` (`api_server.py`) |
| 환경변수 | `FSS_DB_HOST`, `FSS_DB_PORT`, `FSS_DB_USER`, `FSS_DB_PASS`, `FSS_DB_NAME`, `FSS_API_KEY`, `FSS_API_PORT` |

### 서버 배포 구성 (nginx 8443 포트 통합)

**외부 포트 하나(8443)로 모든 서비스를 통합** — 공유기 포트포워딩 1개만으로 운영 가능

```
[외부 접속] https://14.7.14.31:8443/
    │
    ├─ 공유기 포트포워딩: 8443 → 192.168.0.96:8443
    │
    └─ nginx (SSL, port 8443) ─ 리버스 프록시
        │
        ├─ /          → 정적 파일 서빙 (/home/biofl/bfl_lims/*.html)
        ├─ /api/*     → proxy_pass → 127.0.0.1:5001 (시료접수 API)
        ├─ /ocr/*     → rewrite + proxy_pass → 127.0.0.1:5002 (OCR 프록시)
        └─ /fss/*     → rewrite + proxy_pass → 127.0.0.1:5050 (식약처 API)

[내부 Flask 서버] (localhost만 바인딩)
    ├─ receipt_api_final.py  → port 5001 (시료접수 API)
    ├─ ocr_proxy.py          → port 5002 (CLOVA OCR 프록시)
    └─ api_server.py         → port 5050 (식약처 데이터 API + MariaDB)
```

**nginx 설정 파일**: `/etc/nginx/sites-available/bfl_lims`
- SSL 인증서: `/etc/nginx/ssl/incen.crt` / `incen.key`
- OCR 프록시: `client_max_body_size 20m` (이미지 업로드)
- rewrite 규칙: `/ocr/(.*)` → `/$1`, `/fss/(.*)` → `/$1` (접두사 제거)

**환경 감지 (로컬/서버 호환)**:
HTML 파일의 API URL은 실행 환경을 자동 감지하여 분기합니다:
```javascript
// 로컬 개발: 직접 Flask 서버 접속
// 서버 배포: nginx 프록시 경로 사용
var API_BASE = (location.hostname === 'localhost' || location.hostname === '127.0.0.1')
  ? 'http://127.0.0.1:5001'   // 로컬
  : '';                         // 서버 (nginx 프록시)
```

### 서버 업데이트 방법
```bash
# 로컬에서 push 후 서버에서 실행
cd ~/bfl_lims && git pull
```

---

## 공통 모듈: 통합 사이드바 (`js/sidebar.js`)

사이드바 메뉴가 7개 파일에 중복 복사되어 메뉴 누락이 반복되던 문제를 해결하기 위해,
**Single Source of Truth** 방식으로 `js/sidebar.js` 하나에 전체 메뉴를 정의하고 모든 HTML이 이를 참조.

| 역할 | 구현 |
|------|------|
| 메뉴 데이터 | `SIDEBAR_MENU` 배열 (11그룹, 38개 서브메뉴) |
| HTML 렌더링 | `renderSidebar()` — 현재 페이지 자동 감지 → active/expanded 설정 |
| CSS 주입 | `injectSidebarCSS()` — `<style id="sidebar-unified-css">` 자동 삽입 |
| 탭 전환 | `showPage()` 감지 → salesMgmt.html 내부 탭 자동 전환 |
| 아코디언 | `toggleMenu()` 등록 |

**사용하는 HTML 파일** (8개):
- `index.html`, `salesMgmt.html`, `companyRegForm_v2.html`, `sampleReceipt.html`, `itemAssign.html`, `userMgmt.html`, `inspectionMgmt.html`, `adminSettings.html`

**메뉴 변경 시**: `js/sidebar.js`의 `SIDEBAR_MENU` 배열만 수정 → 8개 HTML 전체 자동 반영.

---

## 개발 이력

### 커밋 히스토리

| 커밋 | 설명 |
|------|------|
| `ea7ae70` | 초기 4개 파일 추가 |
| `32e08b2` | 서버에서 모든 파일 복구 — 영업관리, 검사관리, API 관리 |
| `f622ab9` | 대시보드 index.html 복구 |
| `bff3f79` | data 폴더 추가 — 지도 GeoJSON 파일 |
| `a6c8382` | 네비게이션 통일 — 5개 핵심 페이지 사이드바 통합 |
| `d0f4487` | 사이드바 initSidebar 버그 수정 및 검사관리 레이아웃 복구 |
| `c3afa7a` | 영업관리 상단 탭 바 제거 → 사이드바 전용 네비게이션으로 전환 |
| `b6feabe` | 검사관리 식품유형 기능 개선 + README 추가 + 수수료 매핑 데이터 |
| `5a83e3d` | 불필요한 파일 정리 - 설계/비교/테스트/데모 파일 9개 삭제 |
| `7a61f81` | 한글 파일명을 영문 camelCase로 전환 + 내부 참조 수정 |
| `77a3eb4` | BFL_LIMS_planning.md v1.2 업데이트 + 데이터 저장 위치 섹션 추가 |
| `1f4f802` | inspectionMgmt.html 통합 사이드바 적용 + BFL 로고 수정 |
| `ed4c2f8` | 기획서 v2.2 업데이트 — 사이드바 통합 완료 반영 |
| `a31fd5b` | 고정체크 + 워킹데이 처리기한 + 기타설정 페이지 + 메뉴 재구성 |
| `f459914` | 등급 규칙 복합 점수 방식으로 개편 (5개 항목 총 100점) |
| `104217e` | 결제 신뢰도 신호등 규칙 연동 + 계약 형태 조건 편집 가능 |
| `5ac9974` | 사용자 설정을 관리자 메뉴 안으로 통합 |
| `b4b8d84` | 부서 관리 → 부서/팀 관리로 명칭 변경 |
| `e3237be` | 부서/팀 관리를 부서 관리 + 팀 관리로 분리 |
| `e78ecc9` | 사용자 관리 테이블에 팀/입사일/퇴사일 컬럼 추가 + 엑셀 내보내기 + PW초기화 |
| `3475fe7` | 고객사 등록폼 v2 완성: 사용자관리 연동, 이메일 필수, 세금계산서 업체명 모달 |
| `361cfcf` | 고객사 등록폼 파일명 영문 변환 (고객사_등록폼_v2.html → companyRegForm_v2.html) |
| `42056f8` | 고객사 신규등록 버튼을 companyRegForm_v2.html로 연결 |
| `8497880` | README 업데이트: 서버 배포 정보, 고객사 등록폼 v2, OCR 프록시 문서화 |
| `1d794eb` | nginx 8443 포트 통합: 6개 HTML API URL 환경 감지 + nginx 프록시 구성 |
| `22a9d53` | Firebase Firestore 전환 기반 구축: 초기화, 공통 헬퍼, 업로드 도구 |
| `cbd1d02` | adminSettings.html: localStorage → Firestore 전환 |
| `0a27b71` | userMgmt.html: localStorage → Firestore 전환 |
| `c32e291` | userMgmt.html: firebase-ready 이벤트 중복 실행 방지 |
| `3312625` | companyRegForm_v2.html: Firestore 저장 + Firebase Storage 파일 업로드 |
| `47ed408` | companyMgmt.html: localStorage → Firestore 전환 + 선택 삭제 |
| `d2da910` | 업체 데이터 호환성 통일: companyRegForm_v2 ↔ companyMgmt 필드명 표준화 |
| `e0d7604` | companyMgmt·salesMgmt 고객사 목록 통일: Firestore + DEMO 데이터 제거 |
| `fb5c384` | inspectionMgmt.html: 검사관리 6탭 전체 Firestore 영구 저장 |
| `d46928e` | firebase-init.js: Storage SDK 없는 페이지에서 초기화 에러 수정 |
| `f4333f2` | inspectionMgmt.html: firebase-ready 이벤트 리스너를 window로 수정 |
| `7ccddad` | inspectionMgmt.html: 식품유형·항목그룹 컬렉션 배치 저장 방식 전환 |
| `d6fee94` | inspectionMgmt.html: 검사목적 정렬순서 저장 및 정렬 렌더링 수정 |
| `3a6f752` | inspectionMgmt.html: 검사목적 정렬순서 변경 시 기존 항목 자동 밀기 |
| `ceec34b` | inspectionMgmt.html: 접수번호 일련번호 자릿수 1자리부터 선택 가능 |
| `825d99d` | inspectionMgmt.html: 접수번호 세그먼트 저장/복원 + 6자리 옵션 추가 |
| `a90de96` | inspectionMgmt.html: 접수번호 구성 '지부'를 '목적번호'로 변경 |
| `0dd60ef` | inspectionMgmt.html: 일련번호 초기화 설명 동적 표시 |
| `4fbf47e` | inspectionMgmt.html: 접수번호 구분별 설명 추가 + 월/일 표기 개선 |
| `479d081` | inspectionMgmt.html: 월/일 구분 1~12월/1~31일 선택 가능 변경 |
| `7ce2e84` | inspectionMgmt.html: 검사 목적 선택 삭제 + 월/일 선택 기능 추가 |

---

## 완료된 작업 (2026-02-21)

### 검사 목적 선택 삭제 기능 추가

**수정 파일**: `inspectionMgmt.html`
**Firestore 경로**: `settings/inspectionPurposes`
**커밋**: `7ce2e84`

검사 목적 카드 목록에서 여러 항목을 선택하여 일괄 삭제하는 기능 추가.

**HTML 추가** (라인 462~470):
- `☑️ 선택` 버튼 — 선택 모드 진입
- 선택 바: `N개 선택` 카운트 + `전체선택` + `🗑️ 선택 삭제` + `취소` 버튼

**JavaScript 함수** (라인 34420~34457):
| 함수 | 기능 |
|------|------|
| `togglePurposeSelectMode()` | 선택 모드 ON/OFF 토글 (체크박스 표시/숨김) |
| `togglePurposeCheck(e, pidx)` | 개별 카드 선택/해제 (Set으로 관리) |
| `togglePurposeSelectAll()` | 전체 선택/해제 토글 |
| `updatePurposeSelUI()` | 선택 개수 표시 + 체크박스·아웃라인 동기화 |
| `deletePurposeSelected()` | confirm 후 선택 항목 splice → Firestore 저장 |

**동작 방식**:
- `purposeSelectMode` (boolean) — 선택 모드 상태
- `purposeSelected` (Set) — 선택된 인덱스 관리
- 선택 모드에서 카드 클릭 = 체크박스 토글 (openDetail 대신)
- 삭제 시 역순 splice로 인덱스 꼬임 방지
- 삭제 후 번호 자동 재정렬: `rp()`의 forEach idx+1 기반

---

### 접수번호 월/일 구분 선택 가능하도록 변경

**수정 파일**: `inspectionMgmt.html`
**커밋**: `479d081`, `4fbf47e`

**변경 내용**:
- **월 구분**: 고정 "자동(현재 월)" → **1~12월 셀렉트 드롭다운** (기본값: 현재 월)
- **일 구분**: 고정 "자동(현재 일)" → **1~31일 셀렉트 드롭다운** (기본값: 현재 일)
- 접수 시 실제 월/일은 자동 적용되지만, 미리보기에서 선택한 값 표시
- `bp()` 함수에서 `s.v` (선택값) 사용하여 프리뷰 생성

**구분별 설명 텍스트 추가** (라인 34554):
| 세그먼트 타입 | 설명 (ℹ️) |
|-------------|----------|
| `fixed` | 사용자가 지정한 고정 문자 |
| `field` | 소속 분야코드 자동 적용 |
| `year` | 접수 시점의 년도 자동 적용 |
| `month` | 기본: 현재 월 / 접수 시 자동 적용 |
| `day` | 기본: 현재 일 / 접수 시 자동 적용 |
| `serial` | 접수 순서대로 자동 증가 |
| `purpose` | 사용자가 지정한 고정 번호 |

---

### 일련번호 초기화 설명 동적 표시

**수정 파일**: `inspectionMgmt.html`
**커밋**: `0dd60ef`

`updateResetDesc()` 함수 개선 — 현재 세그먼트 구성의 serial 구분 자릿수를 읽어 동적 표시.

**변경 전**: 고정 "0001부터 다시 시작"
**변경 후**: "구분2: 01, 구분3: 00001부터 다시 시작" (실제 세그먼트 구성 반영)

- `dSg.forEach()`로 serial 타입 구분을 순회
- 각 serial의 자릿수(`s.v`)에 맞춰 초기값 계산 (`'1'.padStart(digits,'0')`)
- `renderSegUI()` 끝에 `updateResetDesc()` 호출 추가

---

### 접수번호 구성 '지부'를 '목적번호'로 변경

**수정 파일**: `inspectionMgmt.html`
**커밋**: `a90de96`

기존 `branch`(지부) 타입은 자동증가하는 일련번호와 성격이 다름 — **목적번호는 고정번호(사용자 지정)**, 일련번호는 자동증가. 따라서 `purpose`(목적번호) 타입으로 전면 변경.

**변경 위치**:
| 위치 | 변경 내용 |
|------|----------|
| `renderSegUI()` 프리뷰 블록 | `branch` → `purpose`, 자릿수(`digits`) 기반 padStart |
| `renderSegUI()` 입력 폼 | value 입력 + 1~6자리 select 드롭다운 |
| 타입 select 옵션 라벨 | "지부코드" → "목적번호" |
| `changeSegType()` 기본값 | `purpose: {l:'목적번호', v:'01', digits:'2'}` |
| `bp()` 프리뷰 함수 | purpose 타입 처리 추가 |

**P 객체 세그먼트 구조 예시**:
```javascript
// 02번 축산 - 접수번호: 260700001
segments: [
  {t:'year', v:'2', l:'년도'},
  {t:'purpose', v:'07', digits:'2', l:'목적번호'},
  {t:'serial', v:'5', l:'일련번호'}
]
```

---

### 접수번호 세그먼트 저장/복원 + 6자리 옵션

**수정 파일**: `inspectionMgmt.html`
**Firestore 경로**: `settings/inspectionPurposes` (P 배열 내 각 항목의 `segments`, `segSep`, `segCnt` 필드)
**커밋**: `825d99d`

기존 문제: 검사목적의 접수번호 세그먼트(구분 수, 구분자, 각 구분 타입/값)가 P 객체에 저장되지 않음. `openDetail()` 시 항상 `dInitSeg()`로 기본값(4구분, 하이픈)을 재생성 → 커스텀 설정 유실.

**구현 내용**:

| 단계 | 함수/위치 | 변경 내용 |
|------|----------|----------|
| 1 | 일련번호 select | `['1','2','3','4','5']` → `['1','2','3','4','5','6']` (6자리 옵션 추가) |
| 2 | `saveDetail()` | `p.segments = JSON.parse(JSON.stringify(dSg))`, `p.segSep`, `p.segCnt` 저장 |
| 3 | `openDetail()` | `p.segments` 존재 시 deep copy로 `dSg` 복원 + 구분수/구분자 select 동기화 + `renderSegUI()` |
| 4 | `copyPurpose()` | copy 객체에 `segments`, `segSep`, `segCnt` 포함 (deep copy) |

**동작 흐름**:
1. 사용자가 접수번호 구성 커스텀 → `saveDetail()` → P[idx]에 segments/segSep/segCnt 저장
2. `savePurposesToFirestore()` → Firestore `settings/inspectionPurposes` 에 P 배열 영구 저장
3. 재진입(`openDetail()`) → `p.segments` 확인 → 있으면 복원, 없으면 `dInitSeg()` (하위 호환)
4. 페이지 새로고침 → Firestore에서 P 배열 로드 → segments 포함 복원

---

### 검사목적 일련번호 자릿수 1자리부터 선택 + 정렬순서 기능

**수정 파일**: `inspectionMgmt.html`
**커밋**: `ceec34b`, `3a6f752`, `d6fee94`

- 일련번호 자릿수 선택 범위: 기존 4~5자리 → **1~6자리**
- 검사목적 정렬순서(`p.c`) 변경 시 기존 항목 자동 밀기 로직 추가
- 정렬순서 기반 렌더링 수정 (`P.sort()` → `p.c` 순서)

---

## 완료된 작업 (2026-02-20 ~ 2026-02-21)

### Firebase Firestore 전환 (localStorage → Firestore)

**수정 파일**: 7개 파일 전면 수정
**Firebase SDK**: Firebase compat v10.14.1 (CDN)
**커밋**: `22a9d53` ~ `fb5c384`, `7ccddad`, `f4333f2`, `d46928e`

전체 프로젝트의 데이터 저장소를 **localStorage에서 Firebase Firestore**로 마이그레이션. 브라우저 종속적인 localStorage의 한계(용량 5MB, 브라우저별 독립, 삭제 위험)를 해결하고 클라우드 영구 저장 실현.

#### 1단계: Firebase 기반 구축 (`22a9d53`)

**신규 파일**: `js/firebase-init.js`
```
역할: Firebase 앱 초기화 + Firestore/Storage 전역 변수 생성 + firebase-ready 이벤트 dispatch
```

| 전역 변수 | 용도 |
|----------|------|
| `firebase` | Firebase 앱 인스턴스 |
| `db` | Firestore 인스턴스 (`firebase.firestore()`) |
| `storage` | Firebase Storage 인스턴스 (조건부: Storage SDK 있는 페이지만) |

**커스텀 이벤트**: `firebase-ready`
- `window`에 dispatch (초기에는 `document`였으나 `f4333f2`에서 수정)
- 모든 HTML 페이지에서 `window.addEventListener('firebase-ready', ...)` 로 Firestore 초기화 완료 감지

**Storage 조건부 초기화** (`d46928e`):
```javascript
var storage = (typeof firebase.storage === 'function') ? firebase.storage() : null;
```
- Storage SDK를 포함하지 않는 페이지(`inspectionMgmt.html` 등)에서 초기화 에러 방지

#### 2단계: 각 페이지별 Firestore 전환

| 페이지 | 커밋 | Firestore 경로 | 변경 내용 |
|--------|------|---------------|----------|
| `adminSettings.html` | `cbd1d02` | `settings/adminSettings` | 신호등/등급/공휴일 규칙 Firestore 저장 |
| `userMgmt.html` | `0a27b71` | `users/{docId}` | 사용자 56명 데이터 컬렉션 저장 |
| `companyRegForm_v2.html` | `3312625` | `companies/{docId}` + Storage | 고객사 등록 + 첨부파일 Storage 업로드 |
| `companyMgmt.html` | `47ed408` | `companies/{docId}` | 고객사 목록 Firestore 전환 + 선택 삭제 |
| `companyMgmt + salesMgmt` | `e0d7604` | `companies/{docId}` | 고객사 목록 통일, DEMO 데이터 제거 |
| `inspectionMgmt.html` | `fb5c384` | 다중 경로 (아래 참조) | 검사관리 6탭 전체 Firestore 영구 저장 |

#### 3단계: inspectionMgmt.html 대용량 데이터 처리 (`7ccddad`)

Firestore 단일 문서 1MB 제한으로 식품유형(894카드)·항목그룹(5,695건)·수수료(7,481건)는 컬렉션 배치 방식으로 전환.

**배치 저장 패턴**:
```javascript
// 500건씩 배치 저장 (Firestore batch 제한 500)
const batch = db.batch();
items.forEach((item, i) => {
  batch.set(db.collection('foodTypes').doc('item_' + i), item);
  if ((i + 1) % 500 === 0) { await batch.commit(); batch = db.batch(); }
});
```

| Firestore 컬렉션 | 데이터 | 건수 |
|------------------|--------|------|
| `foodTypes` | 식품유형 카드 데이터 | 894건 |
| `itemGroups` | 항목그룹 데이터 | 5,695건 |
| `inspectionFees` | 수수료 데이터 | 7,481건 |
| `settings/inspectionPurposes` | 검사목적 (P 배열) | 22건 |
| `settings/inspectionFields` | 검사분야 (FIELDS 배열) | 2건 |

#### 업체 데이터 호환성 통일 (`d2da910`)

`companyRegForm_v2.html`과 `companyMgmt.html` 간 필드명 표준화 — 등록폼에서 저장한 데이터를 관리 목록에서 올바르게 표시.

---

## 완료된 작업 (2026-02-20)

### 고객사 등록폼 v2 완성 + 서버 배포

**고객사 등록폼 (`companyRegForm_v2.html`)**:
- 사용자관리(userMgmt.html) USERS_DATA 56명 + localStorage 병합 연동
- 부서 드롭다운: SALES_TEAMS 화이트리스트 4개 (고객지원팀, 마케팅사업부, 고객관리, 지사)
- 접수자 드롭다운: 사용자관리 "접수자" 필드 고유값 15개 (팀명 2개 + 개인명 13개)
- 고객사 담당자 이메일 필수값(*) 표시 추가
- 세금계산서 담당자 업체명: 자유입력 → 모달 선택 방식으로 개선
- 한글 파일명 → 영문(`companyRegForm_v2.html`) 변환 (서버 인코딩 오류 방지)

**salesMgmt.html 연결**:
- 고객사관리 > "+ 신규 등록" 버튼: 내장 폼 → `companyRegForm_v2.html`로 이동

**서버 배포**:
- Git clone → `/home/biofl/bfl_lims`
- nginx SSL 8443 포트 설정 (자체 서명 인증서)
- 공유기 포트포워딩: 8443 → 192.168.0.96:8443
- 접속 URL: `https://14.7.14.31:8443/`

**nginx 8443 포트 통합** (API 리버스 프록시):
- 3개 Flask 서버(5001/5002/5050)를 nginx 프록시로 8443 포트 하나에 통합
- `/api/*` → 시료접수(5001), `/ocr/*` → OCR(5002), `/fss/*` → 식약처(5050)
- 6개 HTML 파일 API URL 환경 감지 분기 적용 (로컬/서버 자동 전환)
- 변경 파일: `sampleReceipt.html`, `companyRegForm_v2.html`, `salesMgmt.html`, `companyMgmt.html`, `admin_api_settings.html`, `admin_collect_status.html`

---

## 완료된 작업 (2026-02-19 ~ 2026-02-20)

### 관리자 설정 — 등급 규칙 복합 점수 시스템

**등급 규칙 JS 완전 재작성** (`adminSettings.html`):
- 기존 단순 구조 → 5개 항목 복합 점수 (총 100점) 체계로 개편
- `GRADE_DEFAULTS`: 5개 카테고리별 기본값 정의
- `GRADE_FIELD_IDS`: 모든 input ID 매핑 (30+ 필드)
- `saveGradeRules()` / `loadGradeRules()` / `resetGradeRules()`: 새 구조에 맞게 재작성

**결제 신뢰도 ↔ 신호등 규칙 실시간 연동**:
- `updatePaymentSignalDisplay()`: 신호등 규칙의 미수금 경과일을 결제 신뢰도 조건에 자동 표시
- 신호등 규칙 저장 시 결제 신뢰도 표시 자동 갱신
- 🟢🔵🟡🟠🔴 아이콘 + 일수 범위 표시

**계약 형태 조건 편집**:
- `.rule-text-input` 클래스로 자유 텍스트 입력 가능
- 기본값: 단발성 거래, 반복 거래, 정기 계약 (연간 계약)
- `conditions` 배열로 localStorage에 저장

### 사이드바 메뉴 재구성

- **사용자 설정 그룹 제거** → 관리자 그룹 안으로 통합 (12그룹 → 11그룹)
- **부서/팀 분리**: 부서 관리 + 팀 관리를 별도 서브메뉴로 분리
- 관리자 서브메뉴 10개: 사용자관리, 부서관리, 팀관리, 권한설정, 기타설정, 대시보드권한, 알림설정, 시스템로그, API수집설정, 수집현황

### 사용자관리 대폭 확장

**테이블 컬럼 추가**:
- 팀(팀명), 입사일, 퇴사일 컬럼 추가
- 56명 사용자 데이터에 `{ 팀명:'', 입사일:'', 퇴사일:'', ...u }` spread 연산자로 일괄 추가

**인라인 편집**:
- `editUser(id)` → `editingUserId` 상태 변수로 편집 행 추적
- 편집 중인 행: 노란 배경(#fffbeb) + 부서/팀/직급/입사일/퇴사일 input 필드
- `saveEditUser(id)` / `cancelEdit()` 으로 저장/취소

**헤더 정렬**:
- `sortBy(key)`: 컬럼 헤더 클릭 → 오름차순/내림차순 토글
- `currentSort = { key, asc }`: 정렬 상태 객체
- `applySortAndRender()`: 정렬 실행 + 화살표(▲/▼) 표시
- 수정 후에도 정렬 상태 유지 → `resetSort()` 버튼으로 초기화

**엑셀 내보내기**:
- `exportExcel()`: CSV UTF-8 BOM(`\uFEFF`) 다운로드
- 파일명: `사용자목록_YYYY-MM-DD.csv`

**비밀번호 초기화**:
- `resetPassword(id)`: confirm → 초기 PW `bfl1234`로 초기화
- 향후 로그인 페이지 연동 예정

---

## 완료된 작업 (2026-02-19)

### inspectionMgmt.html 통합 사이드바 적용 + BFL 로고 수정

- `inspectionMgmt.html` 자체 사이드바(beautiful-mclean) 제거 → `sidebar.js` 통합
- 모든 페이지(7개) 동일한 메뉴 구조로 통일
- BFL 로고 SVG viewBox/letter-spacing 조정으로 글자 잘림 해결
- 사이드바 접힌 상태에서 로고+삼선(☰) 버튼 세로 배치로 개선

## 완료된 작업 (2026-02-18)

### 수수료 데이터 전체 재추출 및 탭 구현

**수수료 데이터 재추출**:
- 엑셀 원본에서 **16개 검사목적** 전체 데이터를 purpose 태그와 함께 재추출
- `js/food_item_fee_mapping.js`: 9,237건 (purpose 필드 포함)
- `js/ref_nonstandard_data.js`: 참고용(기준규격외) 3,374건
- igMap 추론 방식 제거 → `m.purpose` 직접 사용으로 정확도 100%
- dedup 키: `검사목적||검체유형||항목명` (검체유형 포함으로 혼입 완전 해결)

**수수료 탭 (panel-5)**:
- 좌측 검사목적 메뉴 (16개 카테고리) + 우측 카드/리스트 뷰
- 종 단위 통합: 잔류농약(459종/463종/510종), 항생물질(99종/60종/156종) → 검체유형당 1건
- 중복 제거: `검사목적||검체유형||항목명` 기준
- 최종 feeData: **7,481건** / 16개 카테고리
- 검사목적 메뉴 CRUD: 추가(+)/수정(✏️)/삭제(🗑️)
- 수수료 변경 감지: dirty 추적 + 저장바

**수수료 → 식품유형/항목그룹 매칭**:
- 수수료 탭 데이터를 기준으로 식품유형/항목그룹의 항목수수료 동기화
- 식품유형: 자가품질위탁검사용 수수료 우선 매칭 (3,062건 전부 매칭)
- 항목그룹: 검사목적별 매칭 (559건 매칭)

**수수료 탭 상세 필드 비활성화**:
- 검체유형, 규격, 시험법근거, 항목명: readOnly (기초데이터)
- 항목단위: 활성화 유지

### 항목그룹 참고용(기준규격외) 병합

- `REF_NONSTANDARD_ITEM_GROUPS` 3,374건을 `FULL_ITEM_GROUPS`에 병합
- init()에서 itemGroupData 생성 **전에** 병합하도록 코드 순서 수정
- 항목그룹 총: **5,695건** (기존 2,321 + 참고용 3,374)
- 수수료 매칭: 3,318건/3,374건 (98.3%)

### 항목그룹 탭 구조 변경 + CRUD 기능 강화

**렌더링 구조 변경**:
- 검사목적 14개 카테고리 모두 유지
- **항생물질(참고용)/잔류농약(참고용)**: 검체유형별 하위 그룹 유지 (2단 구조)
- **나머지 12개 카테고리**: 검체유형 하위 그룹 제거, 항목명만 flat 리스트로 표시
- `GROUPED_PURPOSES` 상수로 그룹형/flat형 분기 제어

**CRUD 기능**:
- 카테고리 수준: hover 시 ✏️(수정) 🗑️(삭제) 아이콘
  - `editItemGroupPurpose()`: 검사목적 이름 일괄 rename
  - `deleteItemGroupPurpose()`: 카테고리 + 하위 항목 전체 삭제
- 항목 수준: hover 시 ✏️(수정) 🗑️(삭제) 아이콘
  - `deleteItemGroupItem()`: 개별 항목 즉시 삭제
- 기존 상세패널 수정/추가/삭제 기능 유지

**필터 칩 동적 생성**:
- 14개 카테고리 + 건수 동적 표시 (`buildItemGroupChips()`)
- GROUPED_PURPOSES 우선 정렬, 나머지 건수 내림차순

### 기타 개선

- 불필요한 임시 파일 16개 삭제 (_*.py, _*.js, _*.txt, _*.json, *.bak)
- JS 캐시 방지: `?v=20260218` 쿼리스트링 추가
- 검사분야 자동분류: `getDivision()` 함수 (축산_검체유형 54개 목록 기반)

---

## 완료된 작업 (이전)

### inspectionMgmt.html 식품유형 탭 기능 개선

**식품유형 데이터 재추출 (FULL_FOOD_TYPES)**:
- 11개 월별 엑셀(2025_01~11.xlsx)에서 자가품질위탁검사용 데이터 추출
- **시료명 경계 기반 그룹핑**: 시료명별 항목 세트 수집 → 동일 세트를 카드로 묶는 방식
- 이전 방식(검체유형+항목명+규격 중복제거)의 문제 해결: 같은 항목명 다른 규격 (예: 금속성이물 10.0미만/2미만) 분리 표시
- 결과: 894카드, 3,062항목, 220 검체유형

**항목담당자 실데이터 로드**:
- MANAGER_MAP 92개 매핑 (itemAssign.html SAMPLE_ITEMS 기반)
- findManager() 폴백 매칭: 검체유형||항목명 → 항목명만 매치
- 상세패널에서 항목명 변경 시 실시간 담당자 갱신 (updateManagerFromMap)

**UI 개선**:
- 상세패널 제목: "식품유형 -" 제거 → `검체유형 - 항목명` 형식
- 변경 감지: 민트색(#00bfa5) 저장 가이드 + 버튼 강조 + 패널 테두리
- 라벨 태그 관리, 좌우 항목 이동 (◀ ▶), 카드 선택 삭제, 8가지 정렬

**데이터 소스**: 구글드라이브 월별 엑셀 11개 (2025_01 ~ 2025_11.xlsx)

**추출 컬럼** (38컬럼 중 사용):

| 컬럼 | 필드 | 용도 |
|------|------|------|
| E | 검체유형 | 분류 키 |
| M | 항목명 | 검사항목 |
| N | 규격 | 기준값 |
| O | 항목담당자 | 담당자 (최근 월 기준) |
| S | 항목단위 | 단위 |
| Y | 시료명 | 경계 기준 (카드 그룹핑) |
| Z | 검사목적 | 자가품질위탁검사용 필터 |
| AD | 시험법근거 | 시험법 |
| AH | 항목수수료 | 수수료 |

---

## ⚠️ 주의 사항

### 1. 작업 시작 전 읽기/쓰기 권한 허용

Claude Code로 작업하기 전에 **반드시 프로젝트 폴더의 읽기/쓰기 권한을 허용**해야 합니다.

`.claude/settings.local.json` 파일에 다음 권한이 설정되어 있어야 원활한 작업이 가능합니다:

```json
{
  "permissions": {
    "allow": [
      "Read", "Write", "Edit",
      "Bash(git:*)", "Bash(python:*)", "Bash(node:*)", "Bash(npm:*)",
      "Bash(powershell:*)", "Bash(cmd.exe:*)"
    ]
  }
}
```

권한이 설정되지 않으면 매번 파일 읽기/쓰기 시 수동 승인이 필요하여 작업 효율이 크게 떨어집니다.

### 2. 데이터 영속성 — Firebase Firestore 저장 필수

브라우저에서 입력한 데이터는 **반드시 Firebase Firestore에 저장**해야 합니다.

- JavaScript 변수(메모리)에만 저장된 데이터는 **페이지 새로고침 시 모두 초기화**됩니다
- **2026-02-20~21**: 전체 프로젝트 localStorage → Firebase Firestore 마이그레이션 완료
- 모든 데이터 변경 후 Firestore 저장 함수를 반드시 호출
- `js/firebase-init.js`에서 `firebase-ready` 이벤트 발생 후 Firestore 사용 가능

**관련 저장 함수 패턴**:
```javascript
// 데이터 변경 후 반드시 호출
savePurposesToFirestore();   // inspectionMgmt.html — 검사목적
saveFieldsToFirestore();     // inspectionMgmt.html — 검사분야
saveToFirestore();           // adminSettings.html — 신호등/등급/공휴일
saveUsersToFirestore();      // userMgmt.html — 사용자
```

**Firebase 초기화 패턴** (모든 HTML 페이지 공통):
```html
<script src="https://www.gstatic.com/firebasejs/10.14.1/firebase-app-compat.js"></script>
<script src="https://www.gstatic.com/firebasejs/10.14.1/firebase-firestore-compat.js"></script>
<script src="js/firebase-init.js"></script>
<script>
window.addEventListener('firebase-ready', function() {
  // Firestore에서 데이터 로드
  db.collection('settings').doc('inspectionPurposes').get().then(doc => { ... });
});
</script>
```

### 3. 새로운 페이지/기능 개발 시

- 사용자 입력 데이터가 있는 페이지는 `load___()` / `save___ToStorage()` 패턴을 적용할 것
- 초기 로드 시 `localStorage`에서 저장된 데이터를 읽어와 기본 데이터와 병합
- 수정/추가/삭제 후에는 반드시 `localStorage`에 저장

---

## 향후 계획

1. ~~nginx 포트 통합 (8443 하나로 API 프록시 구성)~~ ✅ 완료
2. ~~고객사 등록 DB 저장 API 구현~~ ✅ 완료 (Firebase Firestore로 대체)
3. ~~OCR 프록시 서버 URL 변경 (localhost → 서버 도메인)~~ ✅ 완료 (nginx 프록시로 대체)
4. ~~localStorage → Firebase Firestore 마이그레이션~~ ✅ 완료 (2026-02-20~21)
5. 나머지 메뉴 구현 (성적관리, 재무관리, 통계분석, 문서관리, 재고/시약관리, 공지)
6. 로그인 페이지 구현 + Firebase Authentication 연동
7. 부서 관리 / 팀 관리 페이지 구현
8. 접수번호 실제 발번 로직 구현 (세그먼트 기반 자동 채번)
9. 백엔드 API 연동 + 실제 데이터 연동

---

## 배포 방법

```powershell
# 1. 로컬에서 커밋 & push
git add -A
git commit -m "커밋 메시지"
git push origin main
# → GitHub Pages 자동 배포

# 2. 서버 반영 (SSH 접속 후)
cd ~/bfl_lims && git pull
```

---

## Chrome MCP (Claude in Chrome) 연결 가이드

Claude Code에서 Chrome 브라우저를 제어하여 웹 페이지를 테스트/검증할 때 사용하는 MCP 연결.

### 연결 실패 시 해결 방법 (순서대로 시도)

**1단계: Chrome 확장프로그램 확인**
- `chrome://extensions` 에서 "Claude in Chrome" 확장프로그램 설치/활성화 확인
- 비활성화 상태라면 토글 ON

**2단계: 같은 계정 로그인 확인**
- Claude Desktop과 Chrome의 Claude in Chrome 확장프로그램이 **같은 Anthropic 계정**으로 로그인되어야 함

**3단계: Chrome 완전 재시작**
- Chrome 창을 **모두** 닫기 (백그라운드 프로세스 포함)
- 작업관리자에서 `chrome.exe` 프로세스가 남아있지 않은지 확인
- Chrome 재시작 후 확장프로그램 로드까지 몇 초 대기

**4단계: Claude Desktop 재시작**
- Claude Desktop 완전 종료 후 재시작
- Claude Code (터미널)도 재시작

**5단계: Native Messaging Host 확인**
- 핵심 파일: `chrome-native-host.exe`
- 위치: `C:\Users\{user}\AppData\Local\AnthropicClaude\app-{version}\resources\chrome-native-host.exe`

**6단계: 레지스트리 키 등록 (최종 수단)**
```powershell
# 레지스트리 키 확인
reg query "HKCU\Software\Google\Chrome\NativeMessagingHosts\com.anthropic.claude_browser_extension"

# 키가 없으면 수동 등록 (경로를 실제 버전에 맞게 수정)
reg add "HKCU\Software\Google\Chrome\NativeMessagingHosts\com.anthropic.claude_browser_extension" /ve /d "C:\Users\{user}\AppData\Local\AnthropicClaude\app-{version}\resources\com.anthropic.claude_browser_extension.json" /f
```

### 연결이 끊기지 않도록 하는 방법

1. **Chrome 백그라운드 실행 유지** — Chrome 설정 > 시스템 > "Chrome을 닫을 때 백그라운드 앱 실행 유지" 활성화
2. **절전 모드 비활성화** — PC 절전 모드에 들어가면 프로세스가 중단됨
3. **확장프로그램 업데이트 주의** — Chrome이 확장프로그램을 자동 업데이트하면 연결이 끊어질 수 있음
4. **Claude Desktop 버전 확인** — 업데이트 시 `app-{version}` 경로가 변경되어 레지스트리 재등록 필요
5. **단일 Chrome 프로필 사용** — 하나의 Chrome 프로필에서만 사용
6. **Chrome 탭 최소화 금지** — Chrome이 리소스 절약을 위해 비활성 탭 연결을 끊을 수 있음

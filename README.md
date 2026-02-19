# BioFoodLab LIMS

식품 시험 검사 기관을 위한 **통합 웹 기반 실험실 정보 관리 시스템** (Laboratory Information Management System)

**배포**: https://biofl1411.github.io/bfl_lims/

---

## 기술 스택

| 구분 | 기술 |
|------|------|
| Frontend | Vanilla HTML/CSS/JS, Tailwind CSS (CDN), Chart.js, Leaflet.js |
| Backend | Flask (Python), MariaDB 8.0 |
| 외부 API | VWORLD (지도 타일), Kakao Maps (주소검색/길찾기), 식약처 공공 API (16개) |
| 폰트 | Pretendard, Outfit (Google Fonts) |
| 배포 | GitHub Pages (정적 프론트엔드), bioflsever (Flask API) |

---

## 프로젝트 구조

```
bfl_lims/
├── index.html                      # 대시보드 (메인)
├── inspectionMgmt.html             # 접수관리 > 검사목적관리
├── sampleReceipt.html              # 접수관리 > 접수 등록 (API 연동)
├── itemAssign.html                 # 시험결재 > 항목배정
├── userMgmt.html                   # 관리자 > 사용자관리
├── salesMgmt.html                  # 영업관리 (지도 + 고객사)
├── adminSettings.html              # 관리자 > 기타 설정 (등급규칙/신호등/공휴일)
├── admin_api_settings.html          # 관리자 > API 수집 설정
├── admin_collect_status.html        # 관리자 > 수집 현황
├── receipt_api_final.py             # 시료접수 API 서버 (Flask, port 5001)
├── SETUP_GUIDE.md                   # API 서버 실행 가이드
├── js/
│   ├── sidebar.js                   # ★ 통합 사이드바 (Single Source of Truth) — 전체 메뉴 정의·렌더링·CSS
│   ├── food_item_fee_mapping.js     # 수수료 매핑 데이터 (9,237건, 16개 검사목적, purpose 태그)
│   └── ref_nonstandard_data.js      # 참고용(기준규격외) 데이터 (3,374건)
├── data/
│   ├── sido.json                    # 시도 경계 GeoJSON
│   ├── sigungu.json                 # 시군구 경계 GeoJSON
│   └── dong.json                    # 읍면동 경계 GeoJSON
├── api_server.py                    # Flask REST API 서버
├── collector.py                     # 식약처 데이터 수집기 (cron)
└── deploy.ps1                       # 배포 스크립트
```

### 참고/설계 파일 (운영 불필요)
- `영업관리_설계검토.html` — 영업관리 시스템 설계 문서
- `영업관리_전체시연.html` — 영업관리 전체 기능 데모
- `고객사_등록폼_v2.html`, `고객사_등록폼_시연.html` — 고객사 등록 폼 프로토타입
- `고객사관리_목록vs카드_비교.html` — 목록형 vs 카드형 UI 비교
- `미수금활동_타임라인vs목록_비교.html` — 타임라인 vs 목록 UI 비교
- `A_상단메뉴바.html`, `B_좌측사이드바.html`, `C_상단좌측병행.html` — 레이아웃 테스트

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

### 검사관리 (`inspectionMgmt.html`)
- **6탭 구조**: 검사분야, 검사목적, 식품유형, 검사항목, 항목그룹, 수수료
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

## 데이터 저장소 (localStorage)

| 키 | 용도 | 사용 페이지 |
|----|------|------------|
| `bfl_signal_rules` | 신호등 규칙 (미수금 경과일 5단계) | `adminSettings.html`, `salesMgmt.html` |
| `bfl_grade_rules` | 등급 규칙 (복합 점수 5개 항목) | `adminSettings.html`, `salesMgmt.html` |
| `bfl_holiday_data` | 공휴일 상세 (날짜 + 명칭) | `adminSettings.html` |
| `bfl_holidays` | 공휴일 날짜 배열 | `sampleReceipt.html` |
| `bfl_users_data` | 사용자 관리 수정/추가 데이터 | `userMgmt.html` |

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
| IP | 14.7.14.31 |
| SSH | port 2222 |
| DB | MariaDB 8.0, database: `fss_data` |
| API | http://bioflsever:5060 |
| 환경변수 | `FSS_DB_HOST`, `FSS_DB_PORT`, `FSS_DB_USER`, `FSS_DB_PASS`, `FSS_DB_NAME`, `FSS_API_KEY`, `FSS_API_PORT` |

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

**사용하는 HTML 파일** (7개):
- `index.html`, `salesMgmt.html`, `sampleReceipt.html`, `itemAssign.html`, `userMgmt.html`, `inspectionMgmt.html`, `adminSettings.html`

**메뉴 변경 시**: `js/sidebar.js`의 `SIDEBAR_MENU` 배열만 수정 → 7개 HTML 전체 자동 반영.

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
| *(pending)* | 사용자 관리 인라인 편집 + 헤더 정렬 기능 |

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

### 2. 데이터 영속성 — localStorage 저장 필수

브라우저에서 입력한 데이터(사용자 정보 수정, 신규 추가 등)는 **반드시 `localStorage`에 저장**해야 합니다.

- JavaScript 변수(메모리)에만 저장된 데이터는 **페이지 새로고침 시 모두 초기화**됩니다
- 사용자가 인라인 편집 또는 모달로 입력한 데이터가 저장 없이 사라지는 문제 방지
- 모든 사용자 입력 데이터는 `saveUsersToStorage()` 등 localStorage 저장 함수를 반드시 호출해야 함
- 현재 사용 중인 localStorage 키는 **데이터 저장소 (localStorage)** 섹션 참조

**관련 저장 함수 패턴**:
```javascript
// 데이터 변경 후 반드시 호출
saveUsersToStorage();  // userMgmt.html
saveGradeRules();      // adminSettings.html
saveSignalRules();     // adminSettings.html
```

### 3. 새로운 페이지/기능 개발 시

- 사용자 입력 데이터가 있는 페이지는 `load___()` / `save___ToStorage()` 패턴을 적용할 것
- 초기 로드 시 `localStorage`에서 저장된 데이터를 읽어와 기본 데이터와 병합
- 수정/추가/삭제 후에는 반드시 `localStorage`에 저장

---

## 향후 계획

1. 나머지 메뉴 구현 (성적관리, 재무관리, 통계분석, 문서관리, 재고/시약관리, 공지)
2. 로그인 페이지 구현 + 사용자 인증/권한 시스템
3. 부서 관리 / 팀 관리 페이지 구현
4. 백엔드 API 연동
5. 실제 데이터 연동

---

## 배포 방법

```powershell
# PowerShell 스크립트
.\deploy.ps1

# 또는 수동
git add -A
git commit -m "커밋 메시지"
git push origin main
# → GitHub Pages 자동 배포
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

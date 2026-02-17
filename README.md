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
├── 검사관리.html                    # 접수관리 > 검사목적관리
├── 항목배정.html                    # 시험결재 > 항목배정
├── 사용자관리.html                  # 관리자 > 사용자관리
├── 영업관리_실제화면.html           # 영업관리 (지도 + 고객사)
├── admin_api_settings.html          # 관리자 > API 수집 설정
├── admin_collect_status.html        # 관리자 > 수집 현황
├── js/
│   └── food_item_fee_mapping.js     # 수수료 매핑 데이터 (8,439건)
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

| # | 메뉴 | 상태 | 구현 파일 |
|---|------|------|-----------|
| 1 | 대시보드 | 구현됨 | `index.html` |
| 2 | 영업 관리 | 부분 구현 | `영업관리_실제화면.html` |
| 3 | 접수 관리 | 부분 구현 | `검사관리.html` |
| 4 | 시험 결재 | 부분 구현 | `항목배정.html` |
| 5 | 성적 관리 | 미구현 | — |
| 6 | 재무 관리 | 미구현 | — |
| 7 | 통계 분석 | 미구현 | — |
| 8 | 문서 관리 | 미구현 | — |
| 9 | 재고/시약 관리 | 미구현 | — |
| 10 | 공지 | 미구현 | — |
| 11 | 사용자 설정 | 미구현 | — |
| 12 | 관리자 | 부분 구현 | `사용자관리.html`, `admin_api_settings.html`, `admin_collect_status.html` |

---

## 주요 기능

### 대시보드 (`index.html`)
- KPI 카드 4개 (매출/접수/검사/재고)
- 월별 매출 추이 차트
- 최근 접수 현황 테이블, 검사 진행률, 공지사항

### 영업관리 (`영업관리_실제화면.html`)
- **지도 3단계 드릴다운**: 시도 → 시군구 → 읍면동 (Leaflet + VWORLD 타일)
- **식약처 업소 검색**: 13만+ 업소 DB, 업종별 필터, 페이지네이션
- **카카오맵 연동**: 주소검색, 길찾기
- **9개 서브메뉴**: 고객사관리, 업무일지, 차량일지, 미수금, 거래명세표, 계산서발행, 업체조회, 긴급협조, 세금계산서미발행

### 검사관리 (`검사관리.html`)
- **6탭 구조**: 검사분야, 검사목적, 식품유형, 검사항목, 항목그룹, 수수료
- **식품유형 탭**: 카드뷰 + 아코디언뷰, 검체유형별 카드 분리
- **인라인 데이터**: FULL_FOOD_TYPES (1,166건), 외부 JS 수수료 매핑 (8,439건)
- **상세 패널**: 항목 수정, 라벨 태그 관리, 좌우 항목 이동 (◀ ▶)
- **카드 기능**: 선택 삭제, 8가지 정렬 (기본/항목명/검체유형/담당자/수수료↑↓/항목수↑↓)
- **변경 감지**: 필드 변경 시 "변경사항 있음" 표시 + 저장 버튼 강조

### 항목배정 (`항목배정.html`)
- 담당자 26명 배정 현황 테이블 (이름/부서/파트/직급/배정항목수/진행완료지연/업무부하율)

### 사용자관리 (`사용자관리.html`)
- 56명 사용자 목록, 통계 카드 4개
- 검색, 부서별(9개)/직급별(8개) 필터
- 사용자 추가/수정 모달

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

---

## 현재 진행 중인 작업 (중단된 상태)

### 1. 검사관리.html 식품유형 탭 기능 개선

**브랜치**: `claude/angry-cori` (코드 완료, 브라우저 검증 미완료, 미커밋)

구현된 기능:
- **라벨 태그 관리**: 상세 패널에서 specLabel(자동추출) + customLabels(수동추가) 태그 UI. 입력+Enter 추가, x 클릭 삭제
- **수수료 표시 수정**: feeMap 필터를 자가품질위탁검사용만 → 모든 분류(자가 우선)로 변경. 주황색(#e65100) 13px 강조
- **specLabel 편집/삭제**: 자동 추출 라벨(회색)도 x 버튼으로 삭제 가능
- **상세 패널 좌우 이동**: ◀ ▶ 화살표로 같은 카드 내 항목 이동, N/M 위치 표시
- **저장 가이드라인**: 필드 변경 감지 → "● 변경사항 있음" + 저장 버튼 주황색 강조
- **카드 선택 삭제**: 선택삭제 모드 → 체크박스 선택 후 일괄 삭제
- **카드 정렬 확장**: 수수료 높은/낮은순, 항목수 많은/적은순 추가 (총 8개 정렬)
- **단위 숨기기**: 카드/아코디언 뷰 항목 행에서 항목단위 제거

### 2. FULL_FOOD_TYPES 데이터 모델 변경 (분석 단계)

현재 데이터 구조의 문제점과 변경 방향:

**현재 문제**: FULL_FOOD_TYPES가 검체유형+항목명 기준 중복제거된 마스터 데이터 (1,166건, 220 검체유형)

**올바른 구조**: 검사목적=자가품질위탁검사용만 필터 + **제품/시료명별**로 각각 별도 카드
- 예: `기타수산물가공품 - 깐쇼새우` → 이물, 세균수, 대장균, 성상, 산가, 과산화물가 = 1카드
- 예: `기타수산물가공품 - 사월에매콤주꾸미` → 이물, 대장균 = 별도 1카드

**데이터 소스**: 구글드라이브 월별 엑셀 11개 (2025_01 ~ 2025_11.xlsx)

**컬럼 구조** (총 26컬럼):

| 컬럼 | 필드 |
|------|------|
| A | 접수번호 |
| B | 접수일자 |
| C | 완료예정일 |
| D | 발행일 |
| E | 검체유형 |
| F | 상태 |
| G | 업체명 |
| H | 의뢰인명 |
| I | 업체주소 |
| J | 채취 주소 |
| K | 의뢰업체 |
| L | 관정주주소 |
| M | 항목명 |
| N | 규격 |
| O | 항목담당자 |
| P | 결과입력자 |
| Q | 입력일 |
| R | 분석일 |
| S | 항목단위 |
| T | 시험결과 |
| U | 시험치 |
| V | 성적서결과 |
| W | 판정 |
| X | 채취장소 |
| Y | 제품/시료명 |
| Z | 검사목적 |

**다음 단계**: 11개 엑셀에서 검사목적=자가품질위탁검사용 데이터 추출 → 제품/시료명별 그룹화 → FULL_FOOD_TYPES 재구성

---

## 향후 계획

1. FULL_FOOD_TYPES 데이터 모델 변경 (제품/시료명별 카드 구조)
2. 검사관리.html 기능 개선 브라우저 검증 및 커밋
3. 네비게이션 통일 완료
4. 나머지 메뉴 구현 (성적관리, 재무관리, 통계분석, 문서관리, 재고/시약관리, 공지, 사용자설정)
5. 백엔드 API 연동
6. 사용자 인증/권한 시스템
7. 실제 데이터 연동

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

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
| 외부 API | VWORLD (지도 타일), Kakao (주소검색/길찾기), 국세청 (진위확인), CLOVA OCR, Juso.go.kr (영문주소), 식약처 공공 API (16개) |
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
├── api_server.py                    # Flask REST API 서버 (식약처 데이터, port 5003)
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
- **사업자등록정보 진위확인**: 국세청 API 2단계 (상태조회 + 진위확인)
- **동일 사업자번호 신호등/미수금 승계**: 기존 업체 trafficLight + receivableAmount 자동 승계
- **업체명 모달 선택**: 등록된 업체 목록에서 선택 또는 직접 입력 (담당자 카드 + 세금계산서 담당자)
- **자사 담당자 연동**: `userMgmt.html`의 USERS_DATA + Firestore 병합
  - 부서 드롭다운: 영업 관련 4개만 표시 (고객지원팀, 마케팅사업부, 고객관리, 지사)
  - 접수자 드롭다운: 사용자관리의 "접수자" 필드 고유값 표시 (15개)
- **담당자 카드**: 동적 추가/삭제, 중복 확인, 이메일 필수값(*)
- **세금계산서 담당자**: 1번 담당자 정보 복사 기능, 업체명 모달 선택
- **거래처 등급**: 관리자 설정 등급규칙 기반 자동 산출
- **우편번호 검색**: 카카오 주소 API 연동
- **사업자등록증 영문 정보**: 아코디언 토글 (영문 회사명/주소/업태/종목)
- **원본 문서 저장**: 사업자등록증/인허가문서 Firebase Storage 업로드 → 열람 가능

#### 섹션 1: 기본정보 필드

| 필드명 | HTML id | UI 형태 | 필수 | 규칙 | API 연동 |
|--------|---------|---------|------|------|----------|
| 법인 여부 | `corpType` | radio (법인/개인) | ○ | 법인 선택 시 법인번호 필드 표시 | — |
| 회사명 | `companyName` | text input + 중복확인 버튼 | ○ | `checkCompanyDup()` → Firestore 조회 | Firestore |
| 대표자명 | `regRepName` | text input | ○ | OCR 자동입력 | CLOVA OCR |
| 개업일자 | `regOpenDate` | text input (YYYY-MM-DD) | — | OCR 자동입력 | CLOVA OCR |
| 사업자번호 | `bizNo` | text input + 중복확인/진위확인 버튼 | ○ | `checkBizDup()` + `verifyBizRegistration()` | Firestore + 국세청 API |
| 법인번호 | `regCorpNo` | text input | ○* | *법인 선택 시만 표시, `formatCorpNo()` | — |
| 업태 | `regBizType` | text input | ○ | OCR 자동입력 | CLOVA OCR |
| 종목 | `regBizItem` | text input | ○ | OCR 자동입력 | CLOVA OCR |
| 사업상태 | `regStatus` | select (활동/휴면/해지) | — | — | — |
| 신호등 | `.traffic-dot` | display only | — | 신규=파랑, 동일 사업자번호 시 기존 값 승계 | Firestore |

**사업자등록증 드래그&드롭 영역** (`bizLicFileArea`):
- 파일 타입: image/*, PDF
- 핸들러: `handleBizLicFile(file)` → `_bizLicFile` 전역 변수 저장
- OCR 버튼 (`bizLicOcrBtn`): `runBizLicOCR()` → CLOVA OCR API
- 저장 시 Firebase Storage 업로드: `companies/{id}/biz-license.{ext}`

#### 섹션 2: 주소 필드

| 필드명 | HTML id | UI 형태 | 필수 | 규칙 | API 연동 |
|--------|---------|---------|------|------|----------|
| 우편번호 | `regZipcode` | text (readonly) | ○ | `openPostcodeSearch()` | Daum 우편번호 + Kakao 주소 API |
| 기본주소 | `regAddr1` | text (readonly) | ○ | Daum/OCR 자동입력 | Daum + CLOVA OCR |
| 상세주소 | `regAddr2` | text input | — | 수동 입력 | — |
| Company Name (EN) | `regCompanyNameEn` | text input | — | 수동 입력 | — |
| Representative (EN) | `regRepNameEn` | text input | — | 수동 입력 | — |
| Address (EN) | `regAddrEn` | text input | — | OCR 후 자동 변환 | Juso.go.kr 영문주소 API |

#### 섹션 3: 인허가정보 필드 (동적 카드, 1~N개)

| 필드명 | HTML id | UI 형태 | 필수 | 규칙 | API 연동 |
|--------|---------|---------|------|------|----------|
| 분야 | `licField_[idx]` | select (식품/축산) | ○ | 근거법 배지 자동 표시 | — |
| 영업의 형태 | `licBizForm_[idx]` | combo-select (드롭다운+직접입력) | ○ | OCR 자동입력 | CLOVA OCR |
| 대표자 | `licRepName_[idx]` | text input | ○ | OCR 자동입력 | CLOVA OCR |
| 인허가번호 | `licNo_[idx]` | text input | ○ | OCR 자동입력 | CLOVA OCR |
| 영업소명칭 | `licBizName_[idx]` | text input | ○ | OCR 자동입력 | CLOVA OCR |
| 우편번호 | `licZipcode_[idx]` | text (readonly) | ○ | `openLicPostcode(idx)` | Daum 우편번호 API |
| 기본주소 | `licAddr_[idx]` | text (readonly) | ○ | OCR/Daum 자동입력 | Daum + CLOVA OCR |
| 상세주소 | `licAddrDetail_[idx]` | text input | — | 수동 입력 | — |
| Address (EN) | `licAddrEn_[idx]` | text input | — | 자동 변환 | Juso.go.kr API |

**인허가문서 드래그&드롭 영역** (`licFileArea_[idx]`):
- 핸들러: `handleLicFile(idx, file)` → `_licFiles[idx]` 전역 변수 저장
- OCR 버튼 (`licOcrBtn_[idx]`): `runLicOCR(idx)` → CLOVA OCR API
- 저장 시 Firebase Storage 업로드: `companies/{id}/permits/{ts}_{name}` (licenseIndex 포함)

#### 섹션 4: 고객사 담당자 필드 (동적 카드, 1~N명)

| 필드명 | HTML id | UI 형태 | 필수 | 규칙 | API 연동 |
|--------|---------|---------|------|------|----------|
| 업체명 | `cCompany[n]` | text (readonly) + 모달 | — | `openCompanySelectModal(n)` | — |
| 부서 | `cDept[n]` | text input | — | 수동 입력 | — |
| 담당자(이름) | `cName[n]` | text input | ○ | `checkContactDup()` | Firestore |
| 전화번호 | `cPhone[n]` | text input | ○ | `formatPhone()` | — |
| 이메일 | `cEmail[n]` | email input | ○ | — | — |
| 부서(팀) | `cTeam[n]` | select (4개 팀) | — | `filterRepByTeam(n)` → 접수자 갱신 | Firestore |
| 접수자(담당자) | `cRep[n]` | select | — | 부서 필터 연동, `updateRepBadge(n)` | Firestore |

#### 섹션 5: 세금계산서 담당자 필드

| 필드명 | HTML id | UI 형태 | 필수 | 규칙 |
|--------|---------|---------|------|------|
| 업체명 | `taxCompany` | text (readonly) + 모달 | — | `openCompanySelectModal('tax')` |
| 부서 | `taxDept` | text input | — | 수동 입력 |
| 담당자(이름) | `taxName` | text input | ○ | — |
| 전화번호 | `taxPhone` | text input | ○ | `formatPhone()` |
| 이메일 | `taxEmail` | email input | ○ | — |
| 1번 담당자 복사 | — | button | — | `copyFromContact1()` (자사 담당자 연결 정보 제외) |

#### 섹션 6: 메모/비고

| 필드명 | HTML id | UI 형태 | 필수 | 규칙 |
|--------|---------|---------|------|------|
| 메모 | `regNote` | textarea | — | 특이사항, 계약 조건 입력 |

#### 섹션 7: 변경이력 테이블

| 컬럼 | 필드명 | 설명 |
|------|--------|------|
| 일시 | `log.date` | YYYY-MM-DD HH:mm |
| 변경자 | `log.who` | "시스템 (사업자등록증 OCR)" 또는 사용자명 |
| 변경 내용 | `log.detail` | 【필드명】 "이전값" → "새값" |
| 미수금 | `log.receivable` | 신호등 승계 시 금액 표시 (예: "5,000,000원") |

#### 동일 사업자번호 신호등/미수금 승계 규칙

동일 `bizNo`로 상호만 변경하여 신규 등록 시, 기존 업체의 미수금 상태(신호등)를 자동 승계:

1. 저장 시 `fsGetExistingCompanyByBizNo(bizNo)` 호출 → 기존 업체 조회
2. 기존 업체가 있으면:
   - `trafficLight` 승계 (기존 업체의 신호등 색상)
   - `receivableAmount` 승계 (기존 업체의 미수금 금액)
   - 변경이력에 "동일 사업자번호 기존 업체 [업체명] 신호등: 빨강(위험) 승계" + 미수금 금액 기록
   - 신호등 UI 즉시 업데이트 (파랑 → 승계된 색상)
3. 기존 업체가 없으면: `trafficLight = 'blue'`, `receivableAmount = 0` (기본값)

**신호등 색상 맵**:
| 값 | 색상 | 의미 |
|----|------|------|
| `green` | #4caf50 초록 | 정상 |
| `blue` | #2196f3 파랑 | 양호 (신규 기본값) |
| `yellow` | #ffeb3b 노랑 | 주의 |
| `orange` | #ff9800 주황 | 경고 |
| `red` | #f44336 빨강 | 위험 |

#### Firestore 저장 필드 (`companies` 컬렉션)

| 필드 | 타입 | 설명 |
|------|------|------|
| `company` | string | 회사명 |
| `bizNo` | string | 사업자번호 |
| `repName` | string | 대표자명 |
| `corpType` | string | 법인/개인 |
| `corpNo` | string | 법인번호 |
| `openDate` | string | 개업일자 (YYYY-MM-DD) |
| `bizType` | string | 업태 |
| `bizItem` | string | 종목 |
| `status` | string | 사업상태 |
| `grade` | string | 등급 (신규 'C') |
| `zipcode` | string | 우편번호 |
| `addr1` | string | 기본주소 |
| `addr2` | string | 상세주소 |
| `companyEn` | string | 회사명(영문) |
| `repNameEn` | string | 대표자명(영문) |
| `addrEn` | string | 주소(영문) |
| `licenses[]` | array | 인허가 정보 배열 |
| `contacts[]` | array | 담당자 정보 배열 |
| `taxCompany` | string | 세금계산서 업체명 |
| `taxName` | string | 세금계산서 담당자명 |
| `taxPhone` | string | 세금계산서 연락처 |
| `taxEmail` | string | 세금계산서 이메일 |
| `memo` | string | 메모/비고 |
| `trafficLight` | string | 신호등 색상 (승계 or 'blue') |
| `receivableAmount` | number | 미수금 금액 (승계 or 0) |
| `changeLog[]` | array | 변경 이력 |
| `files.bizLicenseUrl` | string | 사업자등록증 URL |
| `files.bizLicensePath` | string | 사업자등록증 Storage 경로 |
| `files.permitDocs[]` | array | 인허가문서 배열 ({name, url, path, licenseIndex}) |
| `files.ocrResults[]` | array | OCR 결과 배열 ({type, fileName, ocrAt, data}) |
| `regDate` | string | 등록일 (YYYY-MM-DD) |

### 고객사 관리 (`companyMgmt.html`)

접수관리 > 업체등록·수정 페이지. 등록된 고객사 목록 조회/수정/삭제.

- **목록 뷰**: 테이블 + 체크박스 선택, 신호등 색상 표시, 행 배경색 (경고=옅은노랑, 위험=옅은빨강)
- **상세 뷰**: 선택한 업체의 전체 정보 편집
- **삭제 기능**: ⚠️ **이 페이지에서만 고객 삭제 가능** (영업관리에는 삭제 기능 없음)
  - 일괄 삭제: 체크박스 선택 → `bulkDeleteCompanies()` → 모달 확인
  - 단건 삭제: 상세 페이지 → `deleteCompany()` → 모달 확인
  - 권한 체크: `checkDeletePermission()` (현재 placeholder, 추후 등급별 제어)
  - Storage 파일 함께 삭제: `fsDeleteCompanyFiles()` (사업자등록증 + 인허가문서)
- **진위확인**: 사업자번호 옆 "진위확인" 버튼 → `verifyBizRegistration()` → 국세청 API 2단계
- **첨부파일/OCR 열람**: `renderFileViewSection()` — 사업자등록증 원본 보기, OCR 결과 모달
- **인허가 원본 문서**: 각 인허가 카드 하단에 📋 원본 문서 버튼 표시 (`licenseIndex` 기반 매핑)

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
- **6개 아코디언 섹션**: 접수 기본정보, 업체정보, 시료정보, 검사정보, 계산서 정보, 팀별 메모
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

**신호등/미수금 승계 규칙** — 동일 사업자번호(법인번호) 신규 등록 시:

| 조건 | 동작 |
|------|------|
| 동일 `bizNo`로 기존 업체 존재 | `trafficLight` 승계 (기존 업체 신호등 색상 유지) |
| 기존 업체 미수금(`receivableAmount`) > 0 | `receivableAmount` 승계 + 변경이력 기록 |
| 기존 업체 없음 | `trafficLight = 'blue'` (기본), `receivableAmount = 0` |

- **companyMgmt.html** 목록에서 신호등 색상 표시 + 경고/위험 행 배경색 강조
- 통계: 수령 대기(노랑+주황+빨강), 위험(주황+빨강) 건수 표시

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

## 외부 API 모음

프로젝트에서 사용하는 모든 외부 API를 정리합니다.

### 1. CLOVA OCR API (사업자등록증/인허가문서)

| 항목 | 내용 |
|------|------|
| **프록시 서버** | `ocr_proxy.py` (Flask, port 5002) |
| **호출 경로** | `/ocr/api/ocr/biz-license` (사업자등록증), `/ocr/api/ocr/license` (인허가) |
| **메서드** | POST |
| **요청** | `{ version:'V2', requestId, timestamp, images:[{format, name, data(base64)}] }` |
| **CLOVA API URL** | OCR Proxy 내부에서 호출 (NAVER CLOVA OCR) |
| **사용 페이지** | `companyRegForm_v2.html` |
| **버튼 위치** | 사업자등록증 드래그&드롭 영역 내 "OCR 판독" 버튼, 인허가 카드 내 "OCR 판독" 버튼 |
| **함수** | `runBizLicOCR()`, `runLicOCR(idx)` |

### 2. 국세청 사업자등록정보 진위확인 API (공공데이터포털)

| 항목 | 내용 |
|------|------|
| **API 키** | `4553b84e3c3d3816cdfacb285eadeb54f252e8bc48652c3e0eebdaca255fd91c` |
| **메서드** | POST |
| **사용 페이지** | `companyRegForm_v2.html`, `companyMgmt.html` |
| **버튼 위치** | 사업자번호 입력란 옆 "진위확인" 버튼 |
| **함수** | `verifyBizRegistration()` |

**엔드포인트 2개:**

| API | URL | 요청 Body | 응답 |
|-----|-----|----------|------|
| 상태조회 | `https://api.odcloud.kr/api/nts-businessman/v1/status?serviceKey=[KEY]` | `{ b_no: ['사업자번호'] }` | b_stt(상태), tax_type(과세유형), end_dt(폐업일), utcc_yn, tax_type_change_dt, invoice_apply_dt, rbf_tax_type |
| 진위확인 | `https://api.odcloud.kr/api/nts-businessman/v1/validate?serviceKey=[KEY]` | `{ businesses: [{ b_no, start_dt(YYYYMMDD), p_nm(대표자명) }] }` | valid('01'=일치), valid_msg |

### 3. Kakao 주소 검색 API

| 항목 | 내용 |
|------|------|
| **URL** | `https://dapi.kakao.com/v2/local/search/address.json?query=[주소]` |
| **API 키** | `8e5dab09aacd882449bd3865699a9d69` (KakaoAK) |
| **메서드** | GET |
| **헤더** | `Authorization: KakaoAK [KEY]` |
| **응답** | `documents[0].road_address.zone_no`(우편번호), `address_name`(주소) |
| **사용 페이지** | `companyRegForm_v2.html` |
| **버튼 위치** | "우편번호 찾기" 버튼 (사업장 주소, 인허가 주소) |
| **함수** | `openPostcodeSearch()`, `openLicPostcode(idx)`, `searchPostcodeByAddress()` |

### 4. Daum 우편번호 API

| 항목 | 내용 |
|------|------|
| **URL** | `//t1.daumcdn.net/mapjsapi/bundle/postcode/prod/postcode.v2.js` |
| **API 키** | 불필요 (무료) |
| **사용 페이지** | `companyRegForm_v2.html` |
| **호출** | `new daum.Postcode({ oncomplete })` |

### 5. Juso.go.kr 한글→영문 주소 변환 API

| 항목 | 내용 |
|------|------|
| **URL** | `https://business.juso.go.kr/addrlink/addrEngApi.do` |
| **API 키** | `U01TX0FVVEgyMDI2MDIxOTE2MDczMDExNzYyNDM=` (confmKey) |
| **메서드** | GET |
| **파라미터** | `confmKey, currentPage=1, countPerPage=1, keyword=[한글주소], resultType=json` |
| **응답** | `results.juso[0].roadAddr` (영문 도로명 주소) |
| **사용 페이지** | `companyRegForm_v2.html` |
| **버튼 위치** | 자동 호출 (OCR 후 기본주소 변환) |
| **함수** | `convertToEnglishAddress(korAddr, callback)` |
| **폴백** | 내장 `KR_EN_REGION` 지역명 매핑 |

### 6. Kakao Maps API (지도/길찾기)

| 항목 | 내용 |
|------|------|
| **사용 페이지** | `salesMgmt.html` |
| **기능** | 주소검색, 길찾기, 지도 마커 |

### 7. VWORLD 지도 타일

| 항목 | 내용 |
|------|------|
| **사용 페이지** | `salesMgmt.html` |
| **기능** | Leaflet.js 배경 지도 타일 서비스 |

### 8. 식약처 공공 API (식품안전나라 OpenAPI)

| 항목 | 내용 |
|------|------|
| **API 키** | `e5a1d9f07d6c4424a757` |
| **Base URL** | `https://openapi.foodsafetykorea.go.kr/api` |
| **호출 형식** | `{BASE_URL}/{API_KEY}/{서비스ID}/json/{시작}/{끝}` |
| **수집기** | `collector.py` (Firestore 직접 저장) |
| **서비스 수** | 16개 (업소 9 + 품목 2 + 원재료 3 + 변경이력 2) |
| **사용 페이지** | `salesMgmt.html` (업체찾기), `admin_collect_status.html` |

### 인증 정보 요약

| 서비스 | 키/시크릿 | 비고 |
|--------|----------|------|
| **Firebase** apiKey | `AIzaSyDbG7L2gR9UovOYQXE0vv8nbH0_DqqXyyo` | 프로젝트: `bfl-lims` |
| **Firebase** projectId | `bfl-lims` | storageBucket: `bfl-lims.firebasestorage.app` |
| **Firebase** appId | `1:694014042557:web:9162e1e324b7af024072d4` | measurementId: `G-XKTWZLYY93` |
| **Firebase** 서비스 계정 | `serviceAccountKey.json` | 서버 `~/bfl_lims/` (Python 백엔드용) |
| **Firebase** 인증방식 | 익명 인증 (Anonymous Auth) | `firebase-init.js` 에서 자동 처리 |
| **식약처 OpenAPI** | `e5a1d9f07d6c4424a757` | 환경변수: `FSS_API_KEY` |
| **국세청 진위확인** | `4553b84e3c3d3816cdfa...` | 공공데이터포털 serviceKey |
| **Kakao 주소검색** | `8e5dab09aacd882449bd3865699a9d69` | KakaoAK |
| **Juso.go.kr 영문주소** | `U01TX0FVVEgyMDI2MDIxOTE2MDczMDExNzYyNDM=` | confmKey |
| **Naver Clova OCR** Secret | `QWpOSmx5d1NNb01abHhEQ1R3a01ZWUtMYXhxYVNXWnI=` | 환경변수: `CLOVA_OCR_SECRET` |
| **Naver Clova OCR** APIGW | `https://ialgkho4vv.apigw.ntruss.com/custom/v1/50335/4fd4f84e...` | 사업자등록증/인허가/명함 |
| **MariaDB** (레거시) | user: `fss_user` / db: `fss_data` / host: `localhost:3306` | Firestore 이전 완료, 환경변수: `FSS_DB_*` |

---

## OCR 원본 문서 열람 기능

OCR로 업로드한 원본 문서를 저장 후 언제든 열람할 수 있는 기능.

### Firebase Storage 파일 경로

```
companies/{companyId}/
├── biz-license.{ext}          # 사업자등록증 원본
└── permits/
    ├── {timestamp}_{name1}    # 인허가문서 1
    ├── {timestamp}_{name2}    # 인허가문서 2
    └── ...
```

### Firestore 파일 메타 필드 (`companies/{id}`)

| 필드 | 타입 | 설명 |
|------|------|------|
| `files.bizLicenseUrl` | string | 사업자등록증 다운로드 URL |
| `files.bizLicensePath` | string | Storage 경로 (삭제 시 사용) |
| `files.permitDocs[]` | array | 인허가문서 배열 |
| `files.permitDocs[].name` | string | 원본 파일명 |
| `files.permitDocs[].url` | string | 다운로드 URL |
| `files.permitDocs[].path` | string | Storage 경로 |
| `files.permitDocs[].licenseIndex` | number | 연결된 인허가 카드 인덱스 (0-based) |
| `files.permitDocs[].uploadedAt` | string | 업로드 일시 (ISO) |
| `files.ocrResults[]` | array | OCR 인식 결과 |
| `files.ocrResults[].type` | string | 'bizLicense' 또는 'permit' |
| `files.ocrResults[].fileName` | string | 원본 파일명 |
| `files.ocrResults[].ocrAt` | string | OCR 인식 일시 |
| `files.ocrResults[].data` | object | OCR 인식 데이터 |

### 열람 UI (companyMgmt.html)

| 위치 | 기능 | 함수 |
|------|------|------|
| 상단 첨부파일 섹션 | 📄 사업자등록증 원본 보기 버튼 | `renderFileViewSection()` |
| 상단 첨부파일 섹션 | 🔍 OCR 결과 보기 모달 | `openOcrResultModal()` |
| 각 인허가 카드 하단 | 📋 원본 문서 버튼 (해당 인허가에 매핑) | `renderDetailLicenses()` |

### 인허가문서 ↔ 인허가카드 매핑 방식

1. `licenseIndex`가 있는 문서: 해당 인덱스의 인허가 카드에 표시
2. `licenseIndex`가 없는 기존 문서: 순서대로 자동 매핑 (하위 호환)
3. 인허가 카드가 없는데 문서만 있는 경우: 상단 첨부파일 섹션에 표시

### 관련 Firestore Helper 함수

| 함수 | 역할 | Storage 경로 |
|------|------|-------------|
| `fsUploadBizLicense(companyId, file)` | 사업자등록증 업로드 | `companies/{id}/biz-license.{ext}` |
| `fsUploadPermitDoc(companyId, file, null, licenseIndex)` | 인허가문서 업로드 | `companies/{id}/permits/{ts}_{name}` |
| `fsDeleteCompanyFiles(companyId)` | 업체 관련 전체 파일 삭제 | 위 경로 모두 |
| `fsGetCompanyFiles(companyId)` | 파일 메타 조회 | — |

---

## Backend API (`api_server.py`)

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
| `companies/{docId}` | 고객사 등록 데이터 + OCR 결과(`files.ocrResults[]`) | `companyRegForm_v2.html`, `companyMgmt.html` | 컬렉션 |
| `receipts/{docId}` | 접수 데이터 (이전 접수번호 조회용) | `sampleReceipt.html` | 컬렉션 |
| `foodTypes/{docId}` | 식품유형 데이터 (894카드) | `inspectionMgmt.html` | 컬렉션 (배치) |
| `itemGroups/{docId}` | 항목그룹 데이터 (5,695건) | `inspectionMgmt.html` | 컬렉션 (배치) |
| `inspectionFees/{docId}` | 수수료 데이터 (7,481건) | `inspectionMgmt.html` | 컬렉션 (배치) |
| `fss_businesses/{lcns_no}` | 식약처 업소 데이터 (~11,200건) | `salesMgmt.html` | 컬렉션 (인허가번호 키) |
| `fss_products/{auto_id}` | 식약처 품목 데이터 (~661,000건) | `salesMgmt.html` | 컬렉션 |
| `fss_changes/{auto_id}` | 식약처 인허가 변경이력 | `salesMgmt.html` | 컬렉션 |
| `fss_materials/{auto_id}` | 식약처 원재료 | — | 컬렉션 |
| `fss_collection_log/{auto_id}` | API 수집 로그 (날짜/건수/오류) | `admin_collect_status.html` | 컬렉션 |
| `_health/ping` | Firebase 연결 상태 확인 | 전체 | 단일 문서 |

> **대용량 데이터**: Firestore 단일 문서 1MB 제한으로 인해 식품유형·항목그룹·수수료는 **컬렉션 배치 방식**으로 저장 (500건씩 batch.set())

### 식약처 API → Firestore 마이그레이션

MariaDB에서 Firestore로 식약처 공공 API 데이터 전체 이관 완료 (2026-02-22).

| 항목 | 내용 |
|------|------|
| **마이그레이션 스크립트** | `migrate_to_firestore.py` (1회성, MariaDB → Firestore) |
| **자동 수집기** | `collector.py` (Firestore 직접 저장, systemd timer) |
| **서비스 계정 키** | `serviceAccountKey.json` (서버 `~/bfl_lims/`) |
| **Firestore 무료 쓰기 한도** | 일 18,000건 (20,000 중 여유 2,000) |

**수집 API 목록 (16개)**:

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
| API (식약처) | http://127.0.0.1:5003 → nginx `/fss/*` (`api_server.py`) |
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
        └─ /fss/*     → rewrite + proxy_pass → 127.0.0.1:5003 (식약처 API)

[내부 Flask 서버] (localhost만 바인딩)
    ├─ receipt_api_final.py  → port 5001 (시료접수 API)
    ├─ ocr_proxy.py          → port 5002 (CLOVA OCR 프록시)
    └─ api_server.py         → port 5003 (식약처 데이터 API + MariaDB)
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
| `4fdbba2` | 식약처 API 포트 5050→5003 변경 + 포트 사용금지 목록 추가 |
| `a069308` | README.md 대폭 업데이트: Firebase Firestore 마이그레이션 + 접수번호 세그먼트 기능 문서화 |
| `ccdc2db` | sampleReceipt.html: 검사목적 Firestore 연동 + 접수번호 세그먼트 형식 생성 |
| `9bb3e10` | sampleReceipt.html: firebase-auth-compat.js SDK 추가 |
| `92813bf` | sampleReceipt.html: 미정(o:0) 제외 + 접수번호 세그먼트 우선순위 변경 |
| `1ab366a` | sampleReceipt.html: segSep 빈문자열 처리 수정 + 접수번호 형식 라벨 표시 |
| `566628e` | sampleReceipt.html: 이전 접수번호 자동 조회 기능 추가 |
| `68f1faa` | sampleReceipt.html: 이전 접수번호 쿼리 단순화 (복합 인덱스 불필요) |
| `f51c25d` | sampleReceipt.html: 검사목적 드롭다운에 접수번호 형식 라벨 표시 |
| `c712c2d` | sampleReceipt.html: 드롭다운 분야 라벨을 Firestore에서 로드 |
| `1e4b195` | sampleReceipt.html: 커스텀 드롭다운으로 분야 색상 라벨 표시 |
| `cd31f94` | companyRegForm_v2: 매칭 버튼 삭제 + 세금계산서 복사 수정 + OCR 결과 Firebase 저장 |
| `635c3bb` | companyMgmt: 선택 삭제 기능 개선 + 권한 체크 구조 + Storage 파일 정리 |
| `2642f10` | README.md: 2026-02-22 전체 작업 내용 문서화 |
| `e6b523f` | companyMgmt: 상세 페이지에 첨부파일/OCR 결과 보기 기능 추가 |
| `fd4b07e` | companyRegForm_v2: 영문 주소 자동 변환 기능 추가 |
| `a143314` | 영문 주소 변환: 기본주소만 API에 전달 (상세주소 제외) |
| `00ab34b` | companyRegForm_v2: 중복 확인 기능 Firestore 연동 + 저장 전 중복 체크 모달 |
| `c4b2897` | companyRegForm_v2: 저장 전 중복 체크를 사업자번호만으로 변경 |
| `a0fa827` | companyRegForm_v2: 담당자 중복 안내에 부서/접수자 정보 추가 |
| `a5d5318` | companyRegForm_v2: 사업자등록정보 진위확인 기능 추가 |
| `c8a3edc` | companyRegForm_v2: 진위확인 상태조회 전체 필드 표시 |
| `3cd2592` | companyRegForm_v2: 동일 사업자번호 신호등/미수금 승계 기능 |
| `2c16648` | companyMgmt: 인허가 원본 문서를 해당 인허가 카드에 표시 |
| `ca5250e` | companyRegForm: 파일 업로드 버그 수정 — _bizLicFile/_licFiles 변수 사용 |
| `a337939` | companyMgmt: 상세보기에 사업자등록정보 진위확인 기능 추가 |
| `6009964` | 접수등록: 인허가 기반 업체 검색 + Firestore 연동 |
| `a9f1602` | 접수등록: firestore-helpers.js 스크립트 태그 추가 |
| `b1d8e51` | README.md: 식약처 마이그레이션/인증키/업체찾기/접수등록 기록 + 2/23 작업 계획 |
| `9587ba2` | 식품유형 탭 전면 개편: FULL_FOOD_TYPES 삭제 + API 기반 렌더링 |
| `f782256` | 식품군 분류 + 정렬번호 구현 (식품유형 탭 6단계) |
| `996fa77` | 고객사 담당자 + 세금계산서 담당자 휴대폰번호 필드 추가 |
| `41bc542` | 접수등록: 업체정보 이메일/담당자 추가 + 의뢰인 정보→계산서 정보 개편 |

---

## 완료된 작업 (2026-02-22)

### companyRegForm_v2.html — 사업자등록정보 진위확인 + 신호등/미수금 승계

**수정 파일**: `companyRegForm_v2.html`, `js/firestore-helpers.js`
**커밋**: `a5d5318`, `c8a3edc`, `3cd2592`

#### 1. 사업자등록정보 진위확인 (국세청 API)

사업자번호 입력 옆 "진위확인" 버튼 → 2단계 API 조회 결과를 모달로 표시.

- **1단계 상태조회**: 계속사업자/휴업/폐업 + 과세유형/폐업일/세금계산서적용일 등 8개 필드
- **2단계 진위확인**: 대표자명 + 개업일자 일치 여부 → ✅일치 / ❌불일치

#### 2. 동일 사업자번호 신호등/미수금 승계

`submitCompanyForm()` 저장 시 `fsGetExistingCompanyByBizNo()` 호출하여 기존 업체의 trafficLight + receivableAmount 자동 승계.

- 변경이력에 "기존 업체 [업체명] 신호등: 빨강(위험) 승계" + 미수금 금액 기록
- 신호등 UI 즉시 업데이트

### companyMgmt.html — 인허가 원본 문서 + 진위확인

**수정 파일**: `companyMgmt.html`
**커밋**: `2c16648`, `ca5250e`, `a337939`

#### 1. 인허가 원본 문서를 해당 인허가 카드에 표시

`renderDetailLicenses()` 수정 — `files.permitDocs[]`의 `licenseIndex`를 기준으로 각 인허가 카드 하단에 📋 원본 문서 버튼 배치.

- `licenseIndex` 있는 문서: 정확한 인허가 카드에 매핑
- `licenseIndex` 없는 기존 문서: 순서대로 자동 매핑 (하위 호환)

#### 2. 파일 업로드 버그 수정

드래그&드롭으로 올린 파일이 저장되지 않는 버그 수정.
- 원인: `document.getElementById('...').files[0]` 사용 → 드래그&드롭 시 file input에 파일 미설정
- 수정: `_bizLicFile` / `_licFiles[idx]` 전역 변수 사용으로 통일

#### 3. 상세보기 사업자등록정보 진위확인

`companyMgmt.html` 상세 페이지에서도 진위확인 가능하도록 동일 기능 추가.
- Firestore에서 `openDate` 로드하여 진위확인 API에 전달

### companyRegForm_v2.html — 중복 확인 + 영문 주소 + 담당자 중복

**커밋**: `00ab34b`, `c4b2897`, `a0fa827`, `fd4b07e`, `a143314`

- 저장 전 사업자번호 중복 체크 모달 (기존 업체 발견 시 "그래도 저장" 선택 가능)
- 담당자 중복 시 부서/접수자 정보도 함께 안내
- 영문 주소 자동 변환 (`convertToEnglishAddress()`, Juso.go.kr API)
- 기본주소만 API에 전달하여 정확도 향상

### sampleReceipt.html — 검사목적 Firestore 연동 + 커스텀 드롭다운

**수정 파일**: `sampleReceipt.html`
**커밋**: `ccdc2db` ~ `1e4b195` (9개 커밋)
**Firestore 경로**: `settings/inspectionPurposes`, `settings/inspectionFields`, `receipts`

`inspectionMgmt.html`에서 설정한 검사목적 목록과 접수번호 세그먼트 형식이 접수 등록 화면에 실시간 반영되도록 Firestore 직접 연동.

#### 1. 검사목적 드롭다운 Firestore 연동

| 항목 | 내용 |
|------|------|
| **데이터 소스** | Firestore `settings/inspectionPurposes` P 배열 직접 로드 |
| **우선순위** | Firestore(1순위) → API(2순위) → 하드코딩 폴백(3순위) |
| **미정 제외** | `o: 0` (미정) 항목 자동 제외 |
| **분야 필터** | `fields` 배열에서 'F'(식품)/'L'(축산) 포함 여부로 필터 |
| **정렬** | `c`(정렬순서) 기준 오름차순 |

**전역 변수 추가**:
```javascript
let firestorePurposes = [];  // P 배열 (검사목적)
let firestoreFields = [];    // 검사분야 [{code:'F', name:'식품', color:'#4361ee'}, ...]
let firestoreReady = false;  // Firebase 준비 상태
```

**`firebase-ready` 이벤트 리스너**: Firestore에서 검사분야(`settings/inspectionFields`) + 검사목적(`settings/inspectionPurposes`) 로드

#### 2. 커스텀 드롭다운 (분야 색상 라벨)

네이티브 `<select>`는 부분 색상 적용이 불가하여 **div 기반 커스텀 드롭다운** 구현.

| 기능 | 구현 |
|------|------|
| **필드 배지** | Firestore 색상 그대로 적용 (식품 🔵`#4361ee`, 축산 🔴`#ff6b6b`) |
| **배지 소스** | `settings/inspectionFields`에서 `{code, name, color}` 로드 (하드코딩 아님) |
| **드롭다운 UI** | `.custom-select-wrap` → 클릭 시 옵션 목록 표시, 외부 클릭 시 닫힘 |
| **네이티브 동기화** | 숨겨진 `<select>` 값과 동기화 (폼 제출 호환) |

**CSS 클래스**: `.custom-select-wrap`, `.custom-select-display`, `.custom-select-options`, `.custom-select-option`, `.field-label`

**JavaScript 함수**:
| 함수 | 기능 |
|------|------|
| `renderCustomSelect(purposes)` | 커스텀 드롭다운 옵션 렌더링 (분야 배지 포함) |
| `toggleCustomSelect()` | 드롭다운 열기/닫기 토글 |
| `selectCustomOption(value, text, optEl)` | 옵션 선택 → 네이티브 select 동기화 + display 업데이트 |

#### 3. 접수번호 세그먼트 기반 생성

| 항목 | 내용 |
|------|------|
| **우선순위** | 세그먼트(1순위) → API(2순위) → 폴백(3순위) |
| **segSep 수정** | 빈문자열 `""` falsy 문제 해결 (`||` → 명시적 체크) |
| **rcptDesc 표시** | 검사목적 선택 시 접수번호 형식 설명 표시 (`📋 접수번호 형식: ...`) |

**`buildReceiptNoFromSegments(purposeObj, testField)`** — inspectionMgmt.html의 `bp()` 함수와 동일 로직:
- 7가지 세그먼트 타입 처리: `fixed`, `field`, `year`, `month`, `day`, `serial`, `purpose`
- `fieldCodes` 지원: 분야별 고정문자 코드 자동 적용

#### 4. 이전 접수번호 자동 조회

| 항목 | 내용 |
|------|------|
| **함수** | `fetchLatestReceiptNo(testField, testPurpose)` |
| **Firestore 쿼리** | `receipts` 컬렉션에서 `testPurpose` 일치 → 최신 50건 로드 → 클라이언트 필터/정렬 |
| **표시** | `#prev-receipt-no` 입력란에 이전 접수번호 자동 표시 |
| **인덱스** | 단일 필드 쿼리로 복합 인덱스 불필요 |

---

### companyRegForm_v2.html — 매칭 버튼 삭제 + 세금계산서 복사 수정 + OCR Firebase 저장

**수정 파일**: `companyRegForm_v2.html`
**커밋**: `cd31f94`

#### 1. 매칭 버튼 삭제

| 위치 | 변경 |
|------|------|
| Line 413 (정적 HTML) | `<button class="btn-match" onclick="openLicMatchModal(1)">🔗 매칭</button>` 제거 |
| Line 1049 (동적 생성 `addContact()`) | 매칭 버튼 HTML 생성 코드 제거 |
| CSS `.btn-match` | 스타일 제거 |

#### 2. 세금계산서 담당자 복사 수정

`copyFromContact1()` 함수 수정:
- **복사 대상**: 이름, 전화, 이메일, 부서, 업체명 (기본 연락처)
- **제외 대상**: 자사 담당자 연결 정보 (`cTeam1` 부서(팀), `cRep1` 접수자(담당자))
- 토스트 메시지에 "(자사 담당자 연결 정보 제외)" 안내 추가

#### 3. OCR 결과 Firebase 저장

OCR 인식 결과를 전역 변수에 보관 후, 업체 저장 시 Firestore `companies/{id}/files.ocrResults[]`에 함께 저장.

**전역 변수**:
```javascript
var _bizLicOcrResult = null;   // 사업자등록증 OCR 결과
var _licOcrResults = {};        // 인허가 OCR 결과 {idx: {...}}
```

**ocrResult 객체 구조**:
```javascript
{
  type: 'bizLicense' | 'permit',
  fileName: '원본파일명.jpg',
  ocrAt: '2026-02-22T10:30:00Z',
  data: {
    // bizLicense: companyName, repName, bizNo, corpNo, taxType, bizType, bizItem, address, isCorp
    // permit: repName, bizName, licNo, bizForm, field, address
  }
}
```

**저장 흐름**: `runBizLicOCR()` / `runLicOCR()` → 전역 변수에 보관 → `submitCompanyForm()` 시 Firestore update

---

### companyMgmt.html — 선택 삭제 기능 개선

**수정 파일**: `companyMgmt.html`, `js/firestore-helpers.js`
**커밋**: `635c3bb`

기존 브라우저 `confirm()` 대화상자를 **커스텀 확인 모달**로 교체 + 권한 체크 구조 + Storage 파일 정리.

#### 1. 커스텀 삭제 확인 모달

| 모달 | ID | 용도 |
|------|-----|------|
| 일괄 삭제 | `#bulkDeleteModal` | 선택한 N개 업체 삭제 확인 (업체명 + 사업자번호 목록 표시) |
| 단건 삭제 | `#singleDeleteModal` | 상세 페이지에서 1개 업체 삭제 확인 |

**모달 기능**:
- 삭제 대상 업체명 + 사업자번호 스크롤 목록 표시
- 진행률 바 (`del-progress-fill`) 실시간 표시
- 취소 버튼으로 안전하게 중단
- 삭제 중 버튼 비활성화 (중복 실행 방지)

**CSS 클래스**: `.bulk-delete-dialog`, `.bulk-delete-header`, `.bulk-delete-list`, `.del-item`, `.bulk-delete-warn`, `.del-progress-bar`, `.del-progress-fill`

#### 2. 권한 체크 구조 (Placeholder)

```javascript
function checkDeletePermission() {
  // TODO: 사용자 등급 확인 로직 (추후 지정 업무)
  return true;  // 현재는 모든 사용자 허용
}
```

- 일괄 삭제 + 단건 삭제 모두 `checkDeletePermission()` 호출
- 권한 없으면 `toast('⛔ 삭제 권한이 없습니다.')` 표시 + 중단
- **추후 구현 예정**: 사용자 등급별 삭제 권한 제어

#### 3. Storage 파일 정리

`js/firestore-helpers.js`에 `fsDeleteCompanyFiles()` 함수 추가:

```javascript
async function fsDeleteCompanyFiles(companyId) {
  // companies/{id}의 files 필드에서 경로 조회
  // → files.bizLicensePath (사업자등록증) 삭제
  // → files.permitDocs[].path (인허가문서) 각각 삭제
}
```

업체 삭제 시 Firestore 문서뿐 아니라 Firebase Storage 첨부파일도 함께 삭제.

#### 4. 영업관리와 접수관리 역할 분리

| 페이지 | 삭제 기능 | 이유 |
|--------|----------|------|
| `salesMgmt.html` (영업관리) | ❌ 없음 | 업체 정보 삭제는 신중해야 하므로 |
| `companyMgmt.html` (접수관리) | ⭕ 있음 | 권한 있는 담당자만 접근 |

**JavaScript 함수 변경**:
| 함수 | 변경 내용 |
|------|----------|
| `bulkDeleteCompanies()` | `confirm()` → 모달 표시 + 권한 체크 |
| `confirmBulkDelete()` | 신규 — 모달에서 삭제 실행 + 진행률 + Storage 정리 |
| `closeBulkDeleteModal()` | 신규 — 모달 닫기 |
| `deleteCompany()` | `confirm()` → 모달 표시 + 권한 체크 |
| `confirmSingleDelete()` | 신규 — 단건 삭제 실행 + Storage 정리 |
| `closeSingleDeleteModal()` | 신규 — 단건 모달 닫기 |
| `checkDeletePermission()` | 신규 — 권한 체크 placeholder |
| `fsDeleteCompanyFiles()` | 신규 (`firestore-helpers.js`) — Storage 파일 삭제 |

---

### 식약처 API 포트 5050 → 5003 변경 (인센티브 계산기 충돌 해결)

**원인**: nginx `incentive` 설정에서 `listen 5050 ssl`로 인센티브 계산기 전용 포트를 점유하고 있었으나, `bfl-fss-api.service`(식약처 API)도 5050 포트를 사용 → nginx 시작 실패 → **전체 서비스 중단**

**수정 파일 (로컬)**:
| 파일 | 변경 내용 |
|------|----------|
| `api_server.py` | `FSS_API_PORT` 기본값 5050→5003, `serverUrl` localhost:5050→5003 |
| `admin_api_settings.html` | localhost:5050 → localhost:5003 |
| `admin_collect_status.html` | localhost:5050 → localhost:5003 |
| `salesMgmt.html` | localhost:5050 → localhost:5003 (2곳) |
| `README.md` | 포트 정보 업데이트 + 포트 사용 금지 목록 추가 |

**수정 (서버)**:
| 대상 | 변경 내용 |
|------|----------|
| `/etc/nginx/sites-available/bfl_lims` | `/fss/` proxy_pass 5050→5003, `/incentive/` 경로 제거 |
| `/etc/nginx/sites-available/incentive` | `listen 5050 ssl` 인센티브 설정 복원 |
| `/etc/systemd/system/bfl-fss-api.service` | Description port 5050→5003 |
| `/home/biofl/bfl_lims/api_server.py` (서버) | sed로 5050→5003 변경 |

**최종 포트 배치**:
```
[외부 8443] → nginx → /api/  → 5001 (시료접수)
                    → /ocr/  → 5002 (OCR)
                    → /fss/  → 5003 (식약처) ← 변경
[외부 5050] → nginx → listen 5050 ssl → 5051 (인센티브 계산기, 별도 프로그램)
```

### systemd 서비스 등록 (서버 재시작 후 자동 실행)

**신규 서비스 파일 3개** (`/etc/systemd/system/`):
| 서비스 | 포트 | 실행 파일 |
|--------|------|----------|
| `bfl-receipt-api.service` | 5001 | `receipt_api_final.py` |
| `bfl-ocr-proxy.service` | 5002 | `ocr_proxy.py` |
| `bfl-fss-api.service` | 5003 | `api_server.py` |

- `Restart=always`, `RestartSec=5` — 비정상 종료 시 5초 후 자동 재시작
- `enabled` 상태 — 서버 부팅 시 자동 시작

### 식약처 데이터 MariaDB → Firestore 전체 이전

**수정 파일**: `migrate_to_firestore.py` (신규), `collector.py`, `salesMgmt.html`, `js/firestore-helpers.js`
**커밋**: `13ca0f0`, `bb5668b`, `ea91c13`

MariaDB에 저장되던 식약처 공공 API 데이터를 Firestore로 전체 이전하여 **프론트엔드에서 직접 쿼리 가능**하도록 변경.

| 항목 | 내용 |
|------|------|
| **마이그레이션** | `migrate_to_firestore.py` — MariaDB 전체 테이블 → Firestore 1회성 이전 |
| **fss_businesses** | ~11,200건 완료 (인허가번호 `lcns_no` 기준 문서 ID) |
| **fss_products** | ~661,000건 완료 (자동 ID) |
| **fss_changes** | 인허가 변경이력 |
| **fss_materials** | 원재료 정보 |
| **수집기 변경** | `collector.py` — MariaDB 대신 Firestore 직접 저장으로 전환 |
| **프론트엔드 쿼리** | `salesMgmt.html`에서 `db.collection('fss_businesses')` 직접 조회 |
| **count 최적화** | Firestore `count()` 집계 쿼리로 메타데이터 방식 전환 |

### 영업관리 > 업체찾기 (salesMgmt.html) — 지도 UI 개선 + 조회 모달

**수정 파일**: `salesMgmt.html`
**커밋**: `f93ff39`, `df399d5`, `1d07f78`, `8eba765`, `7509da4`, `a210e27`, `1259285`

#### 1. 지도 UI 높이 확대
- 지도 높이: `300px` → `calc(100vh - 200px)` 반응형 적용
- 결과 패널도 동일 높이로 조정

#### 2. 시도/읍면동 필터 수정
- **시도 필터**: `addr_sido` 풀네임 매칭 (서울특별시, 경기도 등 — 기존 "서울", "경기" 약칭 불일치 해결)
- **읍면동 필터**: 행정동↔법정동 매칭 지원 (행정동 이름으로 검색 시 법정동 업소도 표시)
- **findSgCode 수정**: 양주시 클릭 시 남양주시로 잘못 이동하는 버그 해결 (정확한 이름 매칭)
- **matchSigungu 수정**: 지도 클릭 좌표 → 시군구 매칭 시 동일 문제 해결

#### 3. "등록" → "🔍 조회" 버튼 + 품목/변경이력 모달
- FSS 검색 결과의 "+ 등록" 버튼(녹색) → "🔍 조회" 버튼(파란색 `#1565c0`)으로 변경
- `bizDetail(licNo, bizName)` 함수 추가 — Firestore `fss_products` / `fss_changes` 조회

**모달 UI (`#bizDetailModal`)**:
| 탭 | 내용 | Firestore 쿼리 |
|----|------|----------------|
| 품목 | 제품명, 품목유형, 보고일자, 상태, 소비기한 | `fss_products.where('lcns_no','==',licNo)` |
| 변경이력 | 변경일자, 변경전, 변경후, 사유 | `fss_changes.where('lcns_no','==',licNo)` |

- 미수집 업체: "📋 품목 데이터 수집예정" / "📋 변경이력 데이터 수집예정" 안내 메시지 표시
- "📋 고객 등록" 버튼 → `bizReg()` 연결

### 접수등록 > 업체정보 (sampleReceipt.html) — 인허가 기반 업체 검색

**수정 파일**: `sampleReceipt.html`
**커밋**: `6009964`, `a9f1602`

거래처 검색을 목업 API에서 **Firestore companies 컬렉션 실제 검색**으로 변경. 시험분야(식품/축산)에 따라 인허가 정보를 기반으로 업체 필터링.

#### 1. 거래처 검색 변경
- 기존: `/api/companies/search` (하드코딩 3건)
- 변경: `fsSearchCompanies()` (`firestore-helpers.js`) → Firestore `companies` 컬렉션 prefix 검색
- 분야 필터: `licenses[].licField` === 선택된 분야 (식품/축산)

#### 2. 인허가 정보 필드 추가
```
[거래처 *] [검색 입력 ─────────────────── 🔍]
[인허가번호       ] [영업형태          ] [영업소명칭        ]   ← 신규
[계산서업체       ] [사업자번호        ] [대표자            ]
[담당자           ] [전화번호          ] [휴대폰            ] [이메일            ]
[우리측 담당자 ────────────────────────────────────────────────────────────────]
```

| 필드 ID | 라벨 | 소스 |
|---------|------|------|
| `lic-no` | 인허가번호 | `licenses[].licNo` |
| `lic-biz-form` | 영업형태 | `licenses[].licBizForm` |
| `lic-biz-name` | 영업소명칭 | `licenses[].licBizName` |
| `contact-email` | 이메일 | `contactEmail` / `contacts[0].email` |
| `sales-rep` | 우리측 담당자 | `salesRep` / `contacts[0].salesRep` (readonly) |

#### 3. selectCompany() 확장
- 인허가 정보 (인허가번호, 영업형태, 영업소명칭) + 사업자 정보 (계산서업체, 사업자번호, 대표자) **동시 자동 채움**
- 이메일, 우리측 담당자 자동 채움
- 계산서 정보(taxName/taxPhone/taxMobile/taxEmail) 자동 채움
- 분야에 맞는 인허가를 `licenses[]` 배열에서 찾아 매칭

#### 4. 분야 변경 시 초기화
- `onTestFieldChange()` — 분야(식품↔축산) 변경 시 모든 업체정보 필드 초기화

#### 5. 버그 수정
- `firestore-helpers.js` 스크립트 태그가 `sampleReceipt.html`에 누락 → `<head>`에 추가

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
- 3개 Flask 서버(5001/5002/5003)를 nginx 프록시로 8443 포트 하나에 통합
- `/api/*` → 시료접수(5001), `/ocr/*` → OCR(5002), `/fss/*` → 식약처(5003)
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

### 0. 포트 사용 금지 목록 (공유기 포트포워딩 점유)

아래 포트는 **공유기에서 이미 포트포워딩으로 사용 중**이므로 BFL LIMS 개발 시 절대 사용하지 마세요.
새로운 서비스 추가 시 반드시 이 목록을 확인하고, 충돌하지 않는 포트를 선택해야 합니다.

| # | 규칙명 | 프로토콜 | 외부 포트 | 내부 IP | 내부 포트 | 용도 |
|---|--------|---------|----------|---------|----------|------|
| 001 | api | TCP | 8000 | 192.168.0.96 | 8000 | API 서버 |
| 002 | wireguard | UDP | 63964 | 192.168.0.96 | 63964 | VPN |
| 003 | kakaochatbot | TCP | 5000 | 192.168.0.96 | 5000 | 카카오챗봇 |
| 004 | business | TCP | 6001 | 192.168.0.96 | 6001 | 비즈니스 |
| 005 | out | TCP | 2222 | 192.168.0.96 | 22 | SSH (외부 2222→내부 22) |
| 006 | business_demo | TCP | 6005 | 192.168.0.96 | 6005 | 비즈니스 데모 |
| 007 | expiry_date_web | TCP | 7000 | 192.168.0.96 | 7000 | 유통기한 웹 |
| 008 | data_api | TCP | 6800 | 192.168.0.96 | 6800 | 데이터 API |
| 009 | Streamlit | TCP | 8501 | 192.168.0.96 | 8501 | Streamlit |
| 010 | 인센티브 | TCP | 443 | 192.168.0.96 | 443 | 인센티브 (HTTPS) |
| 011 | 인센 | TCP | 5050 | 192.168.0.96 | 5050 | 인센티브 계산기 |
| 012 | 통합림스 | TCP | 8443 | 192.168.0.96 | 8443 | **BFL LIMS** |

**⛔ 사용 금지 포트 요약**: `443`, `2222`, `5000`, `5050`, `6001`, `6005`, `6800`, `7000`, `8000`, `8443`, `8501`, `63964`

**BFL LIMS 내부 Flask 서버 할당 포트** (충돌 없음 확인 완료):
- `5001` — 시료접수 API (`receipt_api_final.py`)
- `5002` — OCR 프록시 (`ocr_proxy.py`)
- `5003` — 식약처 API (`api_server.py`) ← 기존 5050에서 변경 (인센티브 계산기와 충돌 방지)

> **2026-02-22 변경**: 식약처 API 포트를 `5050` → `5003`으로 변경.
> 원인: nginx `incentive` 설정에서 `listen 5050 ssl`로 인센티브 계산기가 5050 포트를 점유 → nginx 시작 실패 → 전체 서비스 중단.
> 인센티브 계산기(`/home/biofl/incen/`)는 BFL LIMS와 별개 프로그램이므로 5050 포트를 양보.

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
10. **삭제 권한 등급별 제어** — `checkDeletePermission()` 구현 (사용자 역할 기반)
11. **OCR 결과 조회 UI** — 업체 상세 페이지에서 OCR 원본 결과 확인 기능

### 완료 작업 (2026-02-23)

#### 작업 0: 식품유형 탭 전면 개편 ✅
- **커밋**: `9587ba2`, `f782256`
- FULL_FOOD_TYPES 하드코딩 3,061줄 삭제 → 식약처 공공 API 4개 기반 렌더링으로 교체
- API별 서브탭(식품공전/개별기준규격/공통기준규격/건강기능식품공전) + 수집 버튼
- 식품군 24개 분류 + 식품군순 정렬 + 식품군 드롭다운 필터
- 카드/리스트 양쪽 뷰 지원, 식품/축산 분야 필터, 검색, 페이지네이션

#### 작업 1: 고객사 담당자 + 세금계산서 담당자 휴대폰번호 추가 ✅
- **커밋**: `996fa77`
- **수정 파일**: `companyMgmt.html`, `companyRegForm_v2.html`, `js/firestore-helpers.js`
- 담당자/세금계산서 섹션: 3열→4열 그리드 (이름/전화/휴대폰/이메일)
- normalizeCompany(): contacts에 `mobile`, flat에 `contactMobile`, 세금계산서에 `taxMobile` 추가
- 변경이력 추적에 mobile 포함

#### 작업 2: 접수등록 업체정보 확장 + 우리측 담당자 ✅
- **커밋**: `41bc542`
- **수정 파일**: `sampleReceipt.html`
- 업체정보에 이메일(`contact-email`) + 우리측 담당자(`sales-rep`, readonly) 필드 추가
- selectCompany(): 이메일, 우리측 담당자 자동 채움

#### 작업 3: 의뢰인 정보 → 계산서 정보로 변경 ✅
- **커밋**: `41bc542`
- **수정 파일**: `sampleReceipt.html`
- "👤 의뢰인 정보" → "🧾 계산서 정보" 섹션 전면 교체
- 계산서 담당 정보 자동 표시: `bill-name`, `bill-phone`, `bill-mobile`, `bill-email` (readonly)
- "계산서 입력 정보 수정하기" 체크박스 → 수정 폼 토글
- 계산서 발행일: 접수일/특정일(date picker)/월말 발행
- 발행 유형: 목적별 구분/합산/기타(textarea)
- Firestore 필드: `billingDateType`, `billingDate`, `billingType`, `billingTypeNote`

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

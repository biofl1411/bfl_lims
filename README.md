# BioFoodLab LIMS

식품 시험 검사 기관을 위한 **통합 웹 기반 실험실 정보 관리 시스템** (Laboratory Information Management System)

**배포 (서버)**: https://14.7.14.31:8443/
**배포 (GitHub Pages)**: https://biofl1411.github.io/bfl_lims/

---

## 절대 규칙: 식약처 통합LIMS 데이터 원칙

> **인터넷 검색으로 수집한 정보를 프로그램에 절대 적용하지 마세요.**

식약처 연동 기능을 구현할 때 반드시 아래 원칙을 따라야 합니다:

1. **식약처 통합LIMS API에서 제공하는 데이터만 사용** — 계산식(nomfrmCn), 양식(codename2), 시험방법, 코드값 등 모든 정보는 반드시 식약처 API 응답에서 가져와야 합니다
2. **인터넷 검색/식품공전/외부 자료로 수식이나 양식을 직접 작성하지 마세요** — 식약처 LIMS가 관리하는 데이터를 우리가 임의로 만들면 안 됩니다
3. **API에서 제공하지 않는 정보는 구현하지 마세요** — API로 조회되지 않는 계산식이나 양식은 식약처 LIMS 웹에서 먼저 등록한 후 API로 가져와야 합니다
4. **프로젝트 내 문서(`mfds_integration/서비스별 가이드/*.pdf`)가 1차 참고 자료** — API 스펙, 파라미터, 호출 방식은 이 PDF 문서를 기준으로 합니다

### 올바른 데이터 흐름
```
식약처 통합LIMS API 조회 → 응답 데이터 → BFL LIMS UI에 표시/사용
```

### 금지되는 흐름
```
인터넷 검색 → 식품공전/논문/블로그 → 수식/양식 직접 코딩 ← 절대 금지
```

---

## 식약처 결과값 처리 규칙 (필수 적용)

모든 검사 결과 입력 UI에서 반드시 `MFDS_RULES` (js/mfds_result_rules.js) 유틸리티를 사용해야 합니다.

### 핵심 규칙
1. **유효자리수 (validCphr)**: 시험항목별 `precision` 필드에 따라 `toFixed(precision)` 반올림 적용
2. **정량한계 (fdqntLimit)**: 측정값 < 정량한계값 → 표기값을 미만표기값(예: "불검출")으로 대체, `fdqntLimitApplcAt: 'Y'`
3. **표기값 (markValue)**: 유효자리수/정량한계 적용된 최종 표시 값 (원본 측정값과 별도)
4. **판정형식 코드 (IM15)**: `최대/최소→01`, `적/부텍스트→02`, `3군법→03`, `2군법→04`, `기준없음→05`
5. **판정용어 코드 (IM35)**: `적합→IM35000001`, `부적합→IM35000002`, `상기실험확인함→IM35000003`
6. **최대값 구분 (IM16)**: `이하→01`, `미만→02`
7. **최소값 구분 (IM17)**: `이상→01`, `초과→02`

### 사용법
```javascript
var processed = MFDS_RULES.processResultValue(rawValue, item, judgmentResult);
MFDS_RULES.applyValidCphr(value, precision)     // 유효자리수 적용
MFDS_RULES.generateMarkValue(value, item)        // 표기값 생성
MFDS_RULES.mapJdgmntFomCode(judgmentType)        // IM15 코드 매핑
MFDS_RULES.mapJdgmntWordCode(judgmentResult)     // IM35 코드 매핑
```

### 데이터 소스
- 시험항목 템플릿: `js/mfds_templates.js` (precision, maxValue, maxValueCode, minValue, minValueCode 등)
- 공통코드: `data/mfds/common_codes.json` (IM15, IM16, IM17, IM35, IM43)
- API 스펙: `mfds_integration/서비스별 가이드/I-LMS-0216_시료검사결과+저장.pdf`

---

## 주요 규칙

- 데이터는 반드시 Firebase Firestore에 저장 (localStorage는 보조/레거시)
- 사이드바 메뉴 변경 시 js/sidebar.js의 SIDEBAR_MENU만 수정
- firebase-ready 이벤트 이후 Firestore 접근
- 포트 사용 금지: 443, 2222, 5000, 5050, 6001, 6005, 6800, 7000, 8000, 8443, 8501, 63964
- BFL 내부 Flask 포트: 5001(시료접수), 5002(OCR), 5003(식약처)
- 커밋 시 한글 커밋 메시지 사용

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
│   ├── ref_nonstandard_data.js      # 참고용(기준규격외) 데이터 (3,374건)
│   ├── mfds-api.js                  # ★ 식약처 통합LIMS API 호출 모듈 (MFDS 네임스페이스)
│   └── mfds-codes.js                # ★ 식약처 코드매핑 데이터 로딩/캐싱/검색 (MFDS_CODES 네임스페이스)
├── img/
│   └── bfl_logo.svg                 # BFL 로고
├── api_server.py                    # Flask REST API 서버 (식약처 데이터, port 5003)
├── collector.py                     # 식약처 데이터 수집기 (cron)
├── mfdsTest.html                    # ★ 식약처 API 연결 테스트 페이지
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
- **8탭 구조**: 검사분야, 검사목적, 품목코드, 식품유형, 시험항목, 기준규격, 참고용, 수수료
- **데이터 저장**: Firebase Firestore 영구 저장 (6탭 모두)
- **검사목적 탭**: 카드 목록 + 상세 패널, 접수번호 세그먼트 구성, 선택 삭제 기능
- **접수번호 세그먼트 시스템**: 구분 수(1~8), 구분자(하이픈/없음), 7가지 타입 지원
  - 타입: 고정문자(`fixed`), 분야코드(`field`), 년도(`year`), 월(`month`), 일(`day`), 일련번호(`serial`), 목적번호(`purpose`)
  - 세그먼트 설정 Firestore 영구 저장/복원 (`P[].segments`, `P[].segSep`, `P[].segCnt`)
  - 각 구분별 ℹ️ 설명 텍스트 표시
  - 월/일: 1~12월/1~31일 셀렉트 드롭다운 (기본값: 현재 월/일)
  - 일련번호 초기화 설명: 세그먼트 구성에 맞게 동적 표시
- **식품유형 탭 (API 기반)**: 식약처 공공 API 실시간 로드
  - 4개 서브탭: 식품공전(60,255건), 개별기준규격(16,104건), 공통기준규격(56,716건), 건강기능식품
  - 카드뷰 + 리스트뷰, 대분류 필터 칩 + 중분류 드롭다운
  - `classifyFoodType()` 키워드 자동 분류: 식품 24개 식품군 + 축산물/수산물/농산물 원재료
  - 엑셀 다운로드 (SheetJS `aoa_to_sheet`, 60,255건 대용량 처리)
- **수수료 탭 — 3개 서브탭**:
  - **수수료 목록**: 7,481건 Firestore 로드, 카드/리스트뷰, 검사목적별 필터, 변경감지+저장
  - **식약처 매핑**: 시험항목코드 ↔ 자가품질위탁검사용 수수료 (166건), Firestore `settings/mfdsFeeMapping`
  - **참고용 매핑**: 참고용(기준규격외) 시험항목별 수수료 (2,171건, 102건 설정), Firestore `settings/refFeeMapping`, 비고 컬럼 지원
- **외부 JS**: `food_item_fee_mapping.js` (9,237건, 16개 검사목적, purpose 태그 포함), `ref_nonstandard_data.js` (참고용(기준규격외) 3,374건)
- **상세 패널**: 항목 수정, 라벨 태그 관리, 좌우 항목 이동 (◀ ▶), 제목에 검체유형 표시
- **카드 기능**: 선택 삭제, 8가지 정렬 (기본/항목명/검체유형/담당자/수수료↑↓/항목수↑↓)
- **변경 감지**: 필드 변경 시 민트색(#00bfa5) "변경사항 있음" 표시 + 저장 버튼 강조 + 패널 테두리

### 시료접수 (`sampleReceipt.html`)
- **API 연동**: `receipt_api_final.py` (Flask, port 5001)와 연동
- **폴백 모드**: API 서버 미실행 시에도 내장 폴백 데이터로 동작
- **서버 상태 표시**: 헤더에 연결 상태 인디케이터 (🟢 연결됨 / 🔴 오프라인)
- **6개 아코디언 섹션**: 접수 기본정보, 업체정보, 시료정보, 검사정보, 계산서 정보, 팀별 메모
- **수수료 Firestore 연동**: `getFeeByCode()` — Firestore `settings/mfdsFeeMapping` 우선 조회, `MFDS_FEE_MAP` JS 폴백
- **참고용 수수료**: `buildRefFeeMap()` — Firestore `settings/refFeeMapping` 우선 조회, mfdsTemplates 폴백
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
| `settings/mfdsFeeMapping` | 자가품질위탁검사용 수수료 매핑 (166건) | `inspectionMgmt.html`, `sampleReceipt.html` | 단일 문서 |
| `settings/refFeeMapping` | 참고용(기준규격외) 수수료 매핑 (2,171건) | `inspectionMgmt.html`, `sampleReceipt.html` | 단일 문서 |
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
        ├─ /fss/*     → rewrite + proxy_pass → 127.0.0.1:5003 (식약처 API)
        └─ /mfds/*    → rewrite + proxy_pass → 127.0.0.1:8080 (식약처 통합LIMS 중간모듈)

[내부 Flask 서버] (localhost만 바인딩)
    ├─ receipt_api_final.py  → port 5001 (시료접수 API)
    ├─ ocr_proxy.py          → port 5002 (CLOVA OCR 프록시)
    └─ api_server.py         → port 5003 (식약처 데이터 API + MariaDB)
[Tomcat 9.0.98] (/home/biofl/tomcat, port 8080)
    └─ LMS_CLIENT_API.war    → 식약처 통합LIMS 중간모듈 (Java Spring)
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

### 다른 PC에서 작업하기 (집/사무실 간 전환)

Claude Code 대화 기록은 **각 PC 로컬에만 저장**되며 클라우드 동기화 안 됨.
코드 파일은 **Git을 통해 수동 동기화** (자동 아님).

#### 최초 세팅 (한 번만)
```bash
git clone https://github.com/biofl1411/bfl_lims.git
cd bfl_lims
claude    # Claude Code 실행
```

#### 매일 작업 시작 시
```bash
cd bfl_lims
git pull origin main    # 최신 코드 받기
claude                  # Claude Code 실행
```

#### 작업 끝나고 퇴근 전
```bash
# deploy.ps1 실행 또는 수동으로:
git add . && git commit -m "작업 내용" && git push origin main
```

#### 동기화 흐름
```
사무실 PC → git push → GitHub → git pull → 집 PC
집 PC    → git push → GitHub → git pull → 사무실 PC
```

> **참고**: `MEMORY.md`는 `.claude/` 폴더 안에 있어 git에 포함 안 됨.
> 새 PC에서는 Claude Code가 `README.md`를 참고하여 프로젝트 맥락을 파악함.

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
| `672463e` | README.md: 2/23 작업 완료 기록 |
| `84b16b8` | API 수집 배치 크기 동적 조절 (I2580/I2600: 1000→500건) |
| `41b9838` | fix: collector.py 디버깅 - auto 모드 방어 로직 + 빈 응답 체크 |
| `85f58af` | fix: 식품유형 카드 그리드 첫 행 빈공간 수정 |
| `e02183c` | feat: 식품공전 API 원본 데이터 엑셀 다운로드 기능 구현 |
| `f56e7fb` | fix: 수수료 탭 로딩 상태 표시 + 엑셀 다운로드 대용량 최적화 |
| `63288ff` | feat: 식품유형 대분류 자동 분류 시스템 구현 (classifyFoodType) |
| `8fc6f1b` | feat: 식품유형 탭에 '식품유형' 대분류 필터 칩 추가 |
| `5723297` | refactor: 식품 분류 체계 전면 개편 — 식약처 24개 식품군 기반 |

---

## 완료된 작업 (2026-02-27)

### 식품유형 데이터 임포트 + 검사관리 탭 추가

**수정 파일**: `inspectionMgmt.html`, `js/sidebar.js`, `js/mfds_templates.js` (신규)
**커밋**: `e2ad0ed`, `f742e67`, `605ce48`

#### 1. 식약처 식품유형 데이터 (XLS → JS → Firestore)
- **원본**: `mfds_integration/(통계) 바이오푸드랩 탬플릿 관리 전체내역_20260227.xls` (922KB)
- **변환**: `js/mfds_templates.js` (2.1MB) — 646개 식품유형, 2,657건 시험항목
- **구조**: `MFDS_TEMPLATES = [{templateName, foodTypeCode, foodTypeName, testItems: [{testItemName, testItemCode, standard, unit, fee, ...}]}]`
- **Firestore**: `mfdsTemplates` 컬렉션 (646 docs) — 임포트 완료

#### 2. 검사관리 식품유형 탭 추가
- 품목코드와 시험항목 사이에 새 탭 추가 (8탭 구조로 확장)
- 아코디언 형태 식품유형 목록 (검색 + 시험항목 테이블)
- Firestore 일괄 임포트 버튼 (400건씩 배치)

#### 3. 시험항목 매핑 자동 채움
- 식약처 한글명 → BFL 항목명 자동 매칭
- BFL 단위 → 식약처 단위코드 자동 매칭
- **커밋**: `8ab40cb`, `9a041cf`, `e6bdc12`

---

### 접수등록: 검사목적별 데이터 소스 분기

**수정 파일**: `sampleReceipt.html`
**커밋**: `aa28c1d`, `6e5d6ed`, `6f49bb6`, `006f1d3`, `eb03839`, `ad6f02b`, `46fb461`

#### 검사목적별 데이터 소스 아키텍처

| 검사목적 | 데이터 소스 | 시험항목 로드 방식 |
|---------|-----------|------------------|
| **자가품질위탁검사용** | `mfdsTemplates` (고시항목 646건) | 식품유형 검색 → 해당 유형의 전체 항목 로드 |
| **참고용(기준규격외)** | `mfds_test_items` (시험항목 2,940건) | 개별 시험항목 검색 → 하나씩 추가 |
| **기타** | `foodTypesMapping` (9,237건) | 검체유형 선택 → 매칭 항목 로드 |

#### 자가품질위탁검사용 모드 (`aa28c1d`, `6e5d6ed`)
- `loadMfdsTemplates()`: Firestore 우선, JS 폴백 (5분 캐시)
- `searchFoodType()`: mfdsTemplates + foodTypesMapping 병합 검색
- `loadInspectionItems()`: mfdsTemplates 우선 → foodTypesMapping 폴백
- 테이블 7열: 체크/No/시험항목/**시험항목코드**/**기준규격**/**단위**/수수료
- 검체유형 input 활성화 + 공전규격 추가 검사 접기 토글

#### 참고용(기준규격외) 모드 (`6f49bb6`, `006f1d3`, `eb03839`)
- `searchRefTestItems()`: MFDS 시험항목 2,940건 검색 (코드/한글명/영문명/별칭)
- `selectRefTestItem()`: 선택한 항목을 테이블에 개별 추가 (중복 방지)
- `buildRefFeeMap()`: mfdsTemplates에서 시험항목코드별 수수료 맵 빌드
- 기준규격/단위는 "-" 표시 (기준규격외이므로 해당 없음)
- `saveSampleToArray()` / `loadSampleFromArray()`: `_refTestItems` 배열로 저장/복원

#### 수수료 계산 개선 (`ad6f02b`)
- `updateFeeSummary()`: 자가품질위탁검사용/참고용(기준규격외) → 테이블 `data-fee` 직접 합산
- `window._feeTotal` 정확히 저장 → 접수현황 수수료 표시

#### 수수료 할인 기능 (`46fb461`)
- 할인 UI: 수수료 총합 아래 할인율(%) / 할인금액(원) 입력란
- `onDiscountRateChange()`: % 입력 → 할인금액 자동 계산
- `onDiscountAmountChange()`: 금액 입력 → 할인율 자동 역계산
- `applyDiscount()`: 할인 적용가 표시 + `window._feeTotal` 갱신
- Firestore 저장: `feeOriginal`, `discountRate`, `discountAmount`, `feeTotal`

---

### 식약처 폴더 (`mfds_integration/`) 파일 목록

```
mfds_integration/
├── (먼저읽어주세요)_개발테스트절차 및 주의사항.pdf
├── (통계) 바이오푸드랩 탬플릿 관리 전체내역_20260227.xls  ← 식품유형 원본 XLS
├── DirectApiTest.java              # API 직접 호출 테스트
├── MacTest.java                    # MAC 주소 확인 테스트
├── O000026.jks                     # 운영 인증서 (바이오푸드랩)
├── O000170.jks                     # 테스트 인증서
├── convert_standards.py            # 표준규격 변환 스크립트
├── 식약처 안내 메일.txt
├── Sample/                         # Java 중간모듈 샘플 소스
│   └── src/gov/mfds/lms_client/
│       ├── Controller/WebApiController.java
│       └── WebApiService.java
├── Sample_중간모듈/                # 중간모듈 추가 샘플
├── 서비스별 가이드/                # API 서비스별 가이드 PDF
├── 코드매핑자료/                   # 13개 Excel 파일
│   ├── 공통코드.xlsx              (383건, IM01~IM42)
│   ├── 품목코드.xlsx              (8,404건, 식품만)
│   ├── 시험항목.xlsx              (2,940건, 식품만)
│   ├── 기준_개별기준규격.xlsx      (15,993건)
│   ├── 기준_공통기준규격.xlsx      (33,739건)
│   ├── 단위.xlsx                  (106건)
│   ├── 부서_사용자목록.xlsx        (5부서, 16사용자)
│   └── 기타...
├── 통합LIMS_WEB_API_검사기관개발가이드_V1.1.pdf
├── 통합LIMS_WEB_API_검사기관개발가이드_개정이력.pdf
├── 통합LIMS_WEB_API_테스트시나리오.xls
└── 통합테스트시나리오_자체의뢰 일반배정 시료별 결재상신.xls
```

---

### Firestore 컬렉션 추가/변경

| 컬렉션 | 건수 | 설명 |
|--------|------|------|
| `mfdsTemplates` | 646건 | 식품유형별 시험항목 (고시항목 기준) — **신규** |
| `mfds_test_items` | 2,940건 | 식약처 시험항목 코드 (기존) |
| `foodTypesMapping` | 9,237건 | 수수료 매핑 (기존, 향후 통합 예정) |

---

### 다음 작업 예정

#### 항목그룹 칩 정리 + 추가 (inspectionMgmt.html)

**대상**: 접수관리 > 검사목적관리 > 항목그룹 탭

| 작업 | 설명 |
|------|------|
| **칩 내 항목 정리** | 기존 칩(검체유형)에 묶인 시험항목 중 불필요 항목 제거/이동 |
| **칩 추가** | 새로운 검체유형(칩) 생성하여 시험항목 묶기 |
| **수수료 매핑** | 항목그룹 내 시험항목에 수수료 매핑 연동 필수 |
| **Firestore 연동** | `itemGroups` 컬렉션 (5,467건) 업데이트 |

**목표**: 항목그룹의 항목명/단위가 식약처 시험항목 코드와 1:1 매칭되도록 정리하여 통계 분석 시 표준 코드 기준 집계 가능하게 함.

---

## 완료된 작업 (2026-02-23)

### inspectionMgmt.html — 식품유형 탭 API 기반 전면 개편

**수정 파일**: `inspectionMgmt.html`
**커밋**: `9587ba2`, `f782256`, `85f58af`, `63288ff`, `8fc6f1b`, `5723297`

#### 1. API 기반 렌더링 전환
- 기존 인라인 `FULL_FOOD_TYPES` (894카드, 3,062항목) 삭제
- Firestore `api_data/{serviceId}/batches/*` 에서 실시간 로드
- 4개 API 서브탭: 식품공전(I0930, 60,255건), 개별기준규격(I0960, 16,104건), 공통기준규격(I2790, 56,716건), 건강기능식품

#### 2. 식품 자동 분류 시스템 (`classifyFoodType`)
- 키워드 기반 자동 분류: PRDLST_NM(품목명)으로 대분류·중분류 자동 판정
- **식약처 24개 식품군** 기반 규칙 (`FOOD_CLASSIFY_RULES`):
  - 과자류·떡류·빵류, 빙과류, 코코아·초콜릿류, 당류, 잼류, 두부류·묵류, 식용유지류, 면류, 음료류, 특수영양식품, 특수의료용도식품, 장류, 조미식품, 절임류·조림류, 주류, 농산가공식품류, 식육가공품, 알가공품, 유가공품, 수산가공식품류, 동물성가공식품류, 벌꿀·화분가공식품류, 즉석식품류, 기타식품류
- **원재료 분류**: 축산물(육류/육류-부위/유원료/알류), 수산물(어류/갑각류/패류·연체류/해조류), 농산물(곡류/두류/서류/엽채류/과채류/근채류/과일류/버섯류/약용식물/유지작물)
- 캐시 기반 성능 최적화 (`_foodClassifyCache`)

#### 3. 대분류 필터 UI
- 필터 칩: 전체 | 식품 | 농산물 | 축산물 | 수산물
- 중분류 드롭다운: 대분류 선택 시 해당 중분류 동적 옵션 + 건수 표시
- 카드/리스트 뷰에 대분류+중분류 색상 뱃지

#### 4. 엑셀 다운로드 기능
- SheetJS (xlsx 0.20.3) CDN 기반 브라우저 XLSX 생성
- `aoa_to_sheet` 대용량 최적화 (60,255건 처리)
- 한글 헤더 매핑 (PRDLST_NM → 품목명 등)

#### 5. 수수료 탭 로딩 상태 표시
- Firestore 7,481건 대량 문서 로딩 시 "데이터 로딩중..." 표시
- 500ms 폴링 기반 자동 렌더링

### 기타 작업 (2026-02-23)

| 작업 | 커밋 | 설명 |
|------|------|------|
| 휴대폰번호 추가 | `996fa77` | 고객사 담당자 + 세금계산서 담당자 휴대폰번호 필드 |
| 접수등록 개편 | `41bc542` | 업체정보 이메일/담당자 추가 + 의뢰인→계산서 정보 개편 |
| collector.py 디버깅 | `41b9838` | auto 모드 방어 로직 + 빈 응답 체크 |
| API 배치크기 조절 | `84b16b8` | I2580/I2600: 1000→500건 (서버 부하 감소) |

---

## 🚧 다음 작업: 접수관리 > 검사목적관리 개편

### 개편 배경

현재 `inspectionMgmt.html`의 "식품유형" 탭은 식약처 API에서 가져온 60,000+건 원시 데이터를 키워드 기반으로 자동 분류하고 있으나, 실무에서 사용하는 **식품공전 식품유형 분류**와 **축산물가공업 검사대상 분류**를 정확히 반영하지 못하는 문제가 있음.

### 개편 목표

1. **식품유형 분류 체계 확립**: 식약처 공식 분류표 기반으로 정확한 분류
   - **식품공전 24개 식품군**: 과자류·떡류·빵류, 빙과류, 코코아·초콜릿류, 당류, 잼류, 두부류·묵류, 식용유지류, 면류, 음료류, 특수영양식품, 특수의료용도식품, 장류, 조미식품, 절임류·조림류, 주류, 농산가공식품류, 식육가공품, 알가공품, 유가공품, 수산가공식품류, 동물성가공식품류, 벌꿀·화분가공식품류, 즉석식품류, 기타식품류
   - **축산물가공업 27개 식품군**: 아이스크림류, 아이스크림믹스류, 동물성유지류, 소시지류, 햄류, 베이컨류, 건조저장육류, 양념육류, 포장육, 식육추출가공품, 간편조리세트, 알가공품, 우유류, 가공유류, 산양유, 발효유류, 버터유, 농축유류, 유크림류, 버터류, 치즈류, 분유류, 유청류, 유당, 유단백가수분해식품, 조제유류

2. **필터 체계 개편**:
   - "식품유형" 필터: 식품공전 24개 + 축산물가공업 27개 식품군 통합
   - 카드 뱃지에 "식품" / "축산" 라벨 구분
   - 원재료(농산물/수산물 등)는 별도 필터 유지
   - 중첩 없음: 각 카드는 하나의 분류에만 소속

3. **classifyFoodType() 함수 리팩토링**:
   - 축산물가공업 27개 식품군 규칙 추가 (우선 매칭)
   - 식품공전 식품군에서 축산 관련 항목(식육가공품, 알가공품, 유가공품) 제거 → 축산으로 이동
   - label 속성 추가: `{ major:'식품유형', label:'식품'|'축산', minor:'...', icon:'...' }`

### 현재 상태 (마지막 커밋: `5723297`)

- 필터 칩: 전체 | 식품 | 농산물 | 축산물 | 수산물
- FOOD_CLASSIFY_RULES: 식품 24개 식품군 + 축산물/수산물/농산물 원재료
- 축산물가공업 27개 식품군 **미반영** (추가 필요)

### 구현 시 참고

- `inspectionMgmt.html` line 1192~: `FOOD_CLASSIFY_RULES` 배열
- `inspectionMgmt.html` line 1314~: `classifyFoodType()` 함수
- `inspectionMgmt.html` line 657~: 필터 칩 HTML
- `inspectionMgmt.html` line 30318~: `filterByMajor()`, `updateMinorFilter()`
- `inspectionMgmt.html` line 32258~: 카드 뱃지 색상맵 (`majorColors`, `majorTextColors`)
- 축산물가공업 검사대상 데이터는 이미지로 제공됨 (27개 식품군, 식품종 포함)

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
| `mfds_common_codes` | 식약처 공통코드 (IM01~IM42) | 383건 |
| `mfds_product_codes` | 식약처 품목코드 (식품) | 8,404건 |
| `mfds_test_items` | 식약처 시험항목 (식품) | 2,940건 |
| `mfds_units` | 식약처 단위코드 (식품) | 106건 |
| `mfds_item_mappings` | BFL↔식약처 항목 매핑 | 사용자 생성 |
| `mfds_cache` | API 응답 캐시 (TTL 기반) | 자동 관리 |

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

## 🔴 식약처 통합LIMS WEB API 연동 (진행 중 — 2026-03-01 갱신)

> **이 섹션은 프롬프트 재시작 시 이어서 작업할 수 있도록 진행 상황을 기록합니다.**
> **실패가 2회 이상 발생하면, `mfds_integration/` 폴더의 전체 내용(PDF 가이드, Sample 소스, 코드매핑 Excel 등)을 정밀히 확인하여 해결하세요.**

### 개요
- 식품 분야만 연동 (의약품/의료기기 제외)
- 업무분야코드: `IM36000001` (식품)
- 아키텍처: `BFL LIMS (HTML+JS)` → `nginx 프록시` → `중간모듈 (Java WAR/Tomcat)` → `식약처 통합LIMS API`
- 문서/샘플 위치: `mfds_integration/` 폴더
- 테스트URL: https://wslims.mfds.go.kr
- 테스트 페이지(식약처): https://wslims.mfds.go.kr/ApiClient/ (시나리오별 수동 테스트 가능)
- 테스트 페이지(자체): https://192.168.0.96:8443/mfdsTest.html (연결 + 전체 API 테스트)

### 서버 환경 (192.168.0.96)
- **Java**: OpenJDK 17.0.18 (설치 완료)
- **Tomcat**: 9.0.98 → `/home/biofl/tomcat` (포트 8080, 수동 설치)
- **WAR 배포**: `/home/biofl/tomcat/webapps/LMS_CLIENT_API` (배포 완료, Spring MVC 정상 로드)
- **인증서**: `/home/biofl/mfds_certs/O000170.jks` (테스트), `O000026.jks` (운영)
- **파일 저장**: `/home/biofl/mfds_files/`
- **Tomcat 시작/종료**: `/home/biofl/tomcat/bin/startup.sh` / `shutdown.sh`
- **setenv.sh**: `JAVA_HOME`, `CATALINA_HOME`, `CATALINA_PID` 설정 완료
- **서버 시간**: UTC (NTP 동기화 활성), 타임존은 인증에 영향 없음 (epoch ms 사용)
- **네트워크**: enp4s0 (MAC: `00:24:54:91:d8:12`, UP 상태)

### application.properties (현재 설정 — 2개 파일)

**1) ResourceBundle용 (실제 인증에 사용됨):**
```properties
# 위치: /home/biofl/tomcat/webapps/LMS_CLIENT_API/WEB-INF/classes/application.properties
keyStore.keyStoreLoc=/home/biofl/mfds_certs/O000170.jks
KeyStore.keyPassWord=mfds2015
keyStore.keyAlias=O000170
fileDownloadPath=/home/biofl/mfds_files
wslimsUrl=https://wslims.mfds.go.kr
keyStore.clientEthName=enp4s0
```

**2) Spring config용 (동일 내용 유지):**
```properties
# 위치: /home/biofl/tomcat/webapps/LMS_CLIENT_API/WEB-INF/config/application.properties
keyStore.keyStoreLoc=/home/biofl/mfds_certs/O000170.jks
KeyStore.keyPassWord=mfds2015
keyStore.keyAlias=o000170
fileDownloadPath=/home/biofl/mfds_files
wslimsUrl=https://wslims.mfds.go.kr
keyStore.clientEthName=enp4s0
```

> **주의**: `ResourceBundle.getBundle("application")`는 `WEB-INF/classes/`에서 읽음.
> `WEB-INF/config/`는 Spring의 `<util:properties>`에서 읽음.
> 두 파일 모두 수정해야 설정이 제대로 반영됨.

### 서버 설정 변경 이력 (WAR 내부 수정 — git 미추적)
| 파일 | 변경 내용 | 날짜 |
|------|----------|------|
| `WEB-INF/spring/appServlet/servlet-context.xml` | `StringHttpMessageConverter` UTF-8 추가 (한글 깨짐 해결) | 2026-02-26 |
| `WEB-INF/web.xml` | `CharacterEncodingFilter` `forceEncoding=true` 추가 | 2026-02-26 |
| `conf/server.xml` (Tomcat) | Connector에 `URIEncoding="UTF-8"` 추가 | 2026-02-26 |
| `WebApiController.class` | 5파라미터 생성자 사용 (clientEthName) | 2026-02-25 |

> **⚠️ 주의**: 이 파일들은 서버의 `/home/biofl/tomcat/` 아래에 있으며, git으로 추적되지 않음.
> WAR를 재배포하면 이 설정이 초기화되므로 반드시 다시 적용해야 함.
> 원본 백업: `WebApiController.class.bak`

### 인증서 정보
| 파일 | alias | 비밀번호 | 용도 | CN | 유효기간 |
|------|-------|----------|------|-----|----------|
| `O000170.jks` | `o000170` | `mfds2015` | 테스트(공용) | CN=O000170 | 2025-12-18 ~ 2029-12-18 |
| `O000026.jks` | `o000026` | `mfds2015` | 운영(바이오푸드랩) | CN=O000026 | 2026-02-25 ~ 2030-02-25 |

> 두 JKS 모두 `alias "1"`에 `*.mfds.go.kr` trustedCertEntry 포함 (mTLS용)
> MD5: O000170.jks = `9dd0538f54c56a6d6d63077fc803824c` (서버/로컬 동일 확인)

### 인증 흐름 (개발가이드 2.4절, 3.2절 기반)

```
검사기관 시스템                    JAVA 중간 모듈                     통합LIMS WEB API
─────────────                   ─────────────                    ────────────────
기관코드/기관ID    ──────→    # 인증값 생성                        기관 전송 데이터 수신
시나리오별 JSON 데이터            - Server MAC 취득
                              - 서버시간(Timestamp)               # 기관 인증 값 수신
                              - 검사기관 인증서(JKS)              # 서버측 인증 값 생성
                              + 기관코드/기관ID                      (서버용/기관코드)
                              + 시나리오별 JSON 데이터
                              ─── SSL 통신 ──────→              기관 인증 값 vs 서버 인증 값 비교
                                                                  │
                                                                  ├→ MAC Address 검증 (1순위)
                                                                  ├→ 인증서 검증 (2순위)
                                                                  └→ 유효성 체크 (3순위)
                                                                  │
서비스 결과 수신    ←─────────── 서비스 결과 수신 ←──────── 결과 전송 / 오류 처리
```

**인증값 생성 과정 (AuthenticateCert.setCertCode):**
1. `data = timestamp + macAddr` (예: `177207770551500-24-54-91-D8-12`)
2. `sign = SHA256withRSA(data, privateKey)` — JKS 개인키로 RSA 서명
3. `certCryp = SHA-256(sign)` — 서명의 해시값
4. `time = RSA_Encrypt(timestamp, publicKey)` — 타임스탬프만 RSA 암호화
5. `certValue = {mfdsLimsId, psitnInsttCode, ..., certCryp, time}` — JSON 조립

**서버측 검증 과정 (추정):**
1. mTLS로 클라이언트 인증서의 CN 확인 → 기관코드 식별
2. `time` 복호화 → 타임스탬프 추출
3. DB에서 해당 기관의 **등록된 MAC 주소** 조회
4. `data = timestamp + 등록된MAC`으로 인증값 재계산
5. 클라이언트가 보낸 `certCryp`와 비교 → 일치하면 인증 성공

> **핵심**: certValue JSON에 macAddr 필드는 없음! 서버는 DB에 등록된 MAC으로 인증값을 재계산하여 비교함.
> **따라서 MAC이 서버에 정확히 등록되지 않으면 인증은 절대 통과할 수 없음.**

### 중간모듈 WAR 구조 (LMS_CLIENT_API)

**배포된 컨트롤러** (`WebApiController.class` — 수정됨):
| 엔드포인트 | 메서드 | 설명 |
|-----------|--------|------|
| `POST /LMS_CLIENT_API/selectUnitTest` | `selectUnitTest(String)` | REST/SOAP API 호출 (JSON) |
| `POST /LMS_CLIENT_API/selectUnitTestFile` | `selectUnitTest(MultipartHttpServletRequest)` | 파일 포함 API 호출 |
| `GET/POST /LMS_CLIENT_API/unitTestFileDownLoad` | `unitTestFileDownLoad(Model)` | 파일 다운로드 |

> **수정사항**: `keyStore.clientEthName` 설정이 있으면 5파라미터 생성자
> `new AuthenticateCert(keyStoreLoc, alias, passWord, clientEthName, context)` 사용.
> 원본 백업: `WebApiController.class.bak`

**요청 JSON 형식** (`selectUnitTest` — REST 방식):
```json
{
  "type": "rest",
  "url": "https://wslims.mfds.go.kr/webService/rest/selectListCmmnCode",
  "param": {"mfdsLimsId": "apitest01", "psitnInsttCode": "O000170", "classCode": "IM36"}
}
```
- `type`: `"rest"` 또는 `"soap"`
- `url`: REST는 `https://wslims.mfds.go.kr/webService/rest/` + 서비스명
- `param`: JSON 객체 (필수 필드: `mfdsLimsId`, `psitnInsttCode`는 반드시 **최상위 레벨**에 포함)

**요청 JSON 형식** (`selectUnitTest` — SOAP 방식):
```json
{
  "type": "soap",
  "url": "/selectListCmmnCode",
  "param": {"mfdsLimsId": "apitest01", "psitnInsttCode": "O000170", "classCode": "IM36"}
}
```
- SOAP에서 `url`은 도메인 없이 서비스명만 (예: `/selectListCmmnCode`)

### 테스트 계정 정보 (O000170 공용 테스트 기관)
- 계정: `apitest01` ~ `apitest20` (기관관리자 권한)
- 웹 로그인 비밀번호: `ODSxcBii` (임시, 마이페이지에서 변경)
- 기관코드: `O000170` (psitnInsttCode)
- 테스트 페이지: https://wslims.mfds.go.kr/ApiClient/
- **주의**: O000170은 여러 기관이 공유하는 테스트 기관. 다른 기관의 테스트 데이터를 수정하지 않도록 주의

### 완료된 작업 ✅
1. ✅ Java 17 설치 확인
2. ✅ Tomcat 9.0.98 설치 (`/home/biofl/tomcat`)
3. ✅ LMS_CLIENT_API.war 배포 (Spring MVC 정상 로드)
4. ✅ 인증서 배치 (`/home/biofl/mfds_certs/`)
5. ✅ application.properties 설정 (테스트 환경, 2개 파일 모두)
6. ✅ `javax.activation-1.2.0.jar` 추가 (Java 17 호환성 해결)
7. ✅ setenv.sh 환경변수 설정
8. ✅ MAC 주소 감지 문제 해결 (clientEthName=enp4s0 설정)
9. ✅ WebApiController 수정 — 5파라미터 생성자로 MAC 명시적 전달
10. ✅ Tomcat 로그로 MAC 포함 확인 (`data:177207770551500-24-54-91-D8-12`)

### ✅ 인증 이슈 해결 완료 (2026-02-26)

**이전 이슈:** "유효하지 않는 인증정보입니다" → **해결됨!**

**원인 2가지:**
1. **MAC 주소 등록 형식 오류**: 식약처 DB에 MAC이 `:` 구분자로 등록되었으나, 실제로는 `-` 구분자가 필요했음
   - 이누리 대리(통합림스)가 2026-02-26 09:30경 MAC 재등록 완료
2. **`webApi: "Y"` 미전송 (가이드 미수록 필수 파라미터)**: 모든 API 호출에 `"webApi":"Y"`를 포함해야 함
   - 이누리 대리가 이메일로 직접 안내한 파라미터 (공식 가이드에 없음!)
   - `mfds-api.js`의 `callApi()`, `testConnection()` 모두 수정 완료

**추가 해결: 한글 깨짐 (인코딩)**
- 증상: API 응답의 한글이 `??` 또는 `-`로 표시됨
- 해결: Spring MVC `servlet-context.xml`에 `StringHttpMessageConverter` UTF-8 추가
  ```xml
  <mvc:annotation-driven>
    <mvc:message-converters>
      <bean class="org.springframework.http.converter.StringHttpMessageConverter">
        <constructor-arg value="UTF-8"/>
      </bean>
    </mvc:message-converters>
  </mvc:annotation-driven>
  ```
- `CharacterEncodingFilter`의 `forceEncoding=true`만으로는 부족, `URIEncoding="UTF-8"`도 불충분

**연결 테스트 결과 (2026-02-26 전체 통과):**
| 테스트 | API | 결과 | 데이터 |
|--------|-----|------|--------|
| 1 | `selectListCmmnCode` (공통코드) | ✅ 성공 | 9건 |
| 2 | `selectListInspctReqest` (의뢰목록) | ✅ 성공 | 236건 |
| 3 | `selectListDept` (부서목록) | ✅ 성공 | 28건 (바이오푸드랩 D003194 포함) |
| 4 | `selectListEmp` (직원목록) | ✅ 성공 | 1건 — API테스터34(apitest34) / L0330159 |
| 5 | `selectListPrdlstLclas` (품목분류대분류) | ✅ 성공 | 18건 |

> 테스트 페이지: `https://192.168.0.96:8443/mfdsTest.html` (연결 테스트 + 전체 API 테스트)

### API 필드명 주의사항 ⚠️

식약처 API 응답 필드명이 직관적이지 않으므로 주의 필요:

| API | 예상했던 필드명 | **실제 필드명** | 비고 |
|-----|---------------|----------------|------|
| `selectListDept` | deptCode, deptName | **codeNo, codeName** | 부서 목록 |
| `selectListEmp` | empCode, empName | **codeNo, codeName** | 직원 목록, `deptCode` 필수 파라미터 |
| `selectListPrdlstLclas` | - | **codeNo, codeName** | `jobRealmCode` 필수 파라미터 |
| `selectListCmmnCode` | - | **codeNo, codeName** | 공통코드 |

> **규칙**: 대부분의 조회 API가 `codeNo` / `codeName` 형태로 응답함.
> 서비스별 필수 파라미터가 다르므로, 호출 전 반드시 서비스별 가이드 PDF 확인 필요.
> 존재하지 않는 서비스명(예: `selectListUser`)은 빈 응답(HTTP 200, body 없음)을 반환하므로 주의.

### 완료된 작업 ✅ (2026-02-26 전체)

**인프라:**
1. ✅ Java 17 설치 확인
2. ✅ Tomcat 9.0.98 설치 (`/home/biofl/tomcat`)
3. ✅ LMS_CLIENT_API.war 배포 (Spring MVC 정상 로드)
4. ✅ 인증서 배치 (`/home/biofl/mfds_certs/`)
5. ✅ application.properties 설정 (테스트 환경, 2개 파일 모두)
6. ✅ `javax.activation-1.2.0.jar` 추가 (Java 17 호환성 해결)
7. ✅ setenv.sh 환경변수 설정
8. ✅ MAC 주소 감지 문제 해결 (clientEthName=enp4s0 설정)
9. ✅ WebApiController 수정 — 5파라미터 생성자로 MAC 명시적 전달
10. ✅ MAC 주소 재등록 (`-` 구분자로 수정, 이누리 대리 확인)
11. ✅ `webApi: "Y"` 필수 파라미터 추가
12. ✅ UTF-8 인코딩 수정 (StringHttpMessageConverter)
13. ✅ nginx 프록시 설정 (`/mfds/` → Tomcat 8080 LMS_CLIENT_API)

**프론트엔드 JS 모듈:**
14. ✅ `js/mfds-api.js` — 식약처 API 호출 모듈
    - `MFDS.callApi(serviceName, params)` → nginx → Tomcat → 식약처 API
    - 래퍼 함수: 의뢰(01xx), 시험(02xx), 성적서(03xx), 진행상황(04xx), 기관(06xx), 공통(08xx)
    - Firestore 캐시 기능 (`mfds_cache` 컬렉션)
    - `selectListEmp`에 `deptCode` 필수 검증 추가
15. ✅ `js/mfds-codes.js` — 코드매핑 데이터 로딩/캐싱/검색 공통 모듈 (522줄)
    - 품목코드 8,404건 / 시험항목 2,940건 / 단위 106건 / 공통코드 383건 Firestore 로드
    - 품목코드 3단 계층 트리 (대분류→중분류→소분류) 빌드
    - 캐스케이딩 드롭다운 + 텍스트 검색 렌더링 (`renderProductPicker`)
    - BFL↔식약처 항목 매핑 CRUD (`mfds_item_mappings` 컬렉션)

**페이지 연동:**
16. ✅ `sampleReceipt.html` — 식약처 품목코드 선택 UI 추가
    - 시료정보 섹션에 3단 캐스케이딩 드롭다운 + 검색 필드
    - 연한 파란색 배경으로 식약처 영역 구분
    - 멀티 시료 전환 시 선택값 복원, 접수 저장 시 `mfdsProductCode`/`mfdsProductName` 포함
    - 접수 이력 불러오기에서 품목코드 복원
17. ✅ `inspectionMgmt.html` — 시험항목 브라우저 + 매핑 모달 추가
    - Panel 3: 시험항목 2,940건 검색/테이블/페이지네이션 (50건/페이지)
    - 매핑 모달: 식약처 시험항목 ↔ BFL 항목명 연결 + 단위코드 선택
    - Panel 4: 항목그룹 4개 렌더링 위치 모두에 매핑 뱃지(✅/⚠) + 🔗 버튼
    - Excel 매핑 내보내기 기능
18. ✅ `mfdsTest.html` — 식약처 API 연결 테스트 페이지
    - 연결 테스트 (5항목 체크리스트) + 전체 API 테스트 (5개 API)
19. ✅ Firestore 코드매핑 데이터 업로드 완료
    - `mfds_common_codes` 383건, `mfds_product_codes` 8,404건
    - `mfds_test_items` 2,940건, `mfds_units` 106건

**추가 완료 (2026-02-27~28):**

20. ✅ `js/mfds_templates.js` — 식약처 시험항목 템플릿 데이터 (74,903줄)
    - 식약처 코드매핑 `mfdsTemplates` XLS → JS 변환 (646 템플릿, 2,657개 시험항목)
    - Firestore `mfdsTemplates` 컬렉션 임포트 기능
    - 접수등록에서 식품유형 선택 시 시험항목 자동 로드에 활용
21. ✅ `js/mfds_result_rules.js` — 식약처 결과값 처리 규칙 모듈 (157줄)
    - `applyValidCphr(value, precision)` — 유효자리수 반올림
    - `applyFdqntLimit(value, item)` — 정량한계 미만 시 불검출 처리
    - `generateMarkValue(value, item)` — 표기값 생성 (유효자리수 + 정량한계 통합)
    - `mapJdgmntFomCode(type)` — IM15 판정형식 코드 매핑 (최대/최소→01, 적/부→02 등)
    - `mapJdgmntWordCode(result)` — IM35 판정용어 코드 매핑 (적합→IM35000001 등)
    - `mapMaxValueSeCode/mapMinValueSeCode` — IM16/IM17 이하/미만/이상/초과 구분
    - `processResultValue(raw, item, judgment)` — 전체 처리 통합 함수
22. ✅ `js/mfds-fee-mapping.js` — 수수료 매핑 데이터 (178줄)
    - 식약처 수수료 체계 기반 검사목적별 수수료 매핑
23. ✅ `js/food_types_qc.js` — 식품유형 품질관리 모듈 (1,031줄)
    - 식품유형 데이터 무결성 검증, 중복 체크
24. ✅ `testResultInput.html` — 검사결과 입력 페이지 전면 신규 구현 (2,010줄)
    - 접수현황에서 접수건 선택 → 시료별 시험항목 렌더링
    - 측정값 입력 → MFDS_RULES 자동 적용 (유효자리수, 정량한계, 표기값)
    - 자동판정 (적합/부적합/검출/불검출) — 최대값/최소값 기준 비교
    - Firestore 저장/복원 (`testResults` 컬렉션)
    - 식약처 전송 기능: 시험일지 등록(0209) + 결과 전송(0216) 2단계
    - 전송 전 확인 모달 (항목별 측정값/표기값/판정 테이블 미리보기)
25. ✅ `js/mfds_diary_form.js` — 시험일지 양식 뷰어 모듈 (198줄)
    - API 체인: exprIemCode → 0241(selectListExprMth) → exprMthSn → 0242(selectListExprDiaryForm) → codename2(HTML)
    - 사용범위코드 3단계 조회: 개인(SY05000003) → 부서(SY05000002) → 기관(SY05000001)
    - `renderInteractive(html, container)` — 빈 `<td>` 셀을 contenteditable로 변환
    - `collectFormHtml(container)` — 편집된 HTML 수집 (clean)
    - 결과 캐시 지원 (API 재호출 방지)
    - testResultInput.html에 [양식] 버튼으로 연동 — 항목별 시험일지 양식 조회/표시
    - **운영 서버 검증 완료**: 납(B10001) → 중금속_납_일지 [개인] 양식 정상 조회 확인

**페이지 연동 (2026-02-27~28):**

26. ✅ `sampleReceipt.html` — 식약처 연동 확장
    - 검사목적별 UI 분기: 자가품질위탁검사용 → 식약처 연동 모드 활성화
    - 식품유형(mfdsTemplates) 선택 시 시험항목 자동 로드
    - 참고용(기준규격외) MFDS 시험항목 2,940건 검색/추가 기능
    - 수수료 계산: 참고용 + 자가품질위탁검사용 테이블 직접 합산
27. ✅ `inspectionMgmt.html` — 수수료 식약처 코드 매핑 서브탭 추가
28. ✅ `itemAssign.html` — 시험일지 관련 API 9개 래퍼 추가 + 일지 관리 UI 구현

### ✅ 31단계 테스트 시나리오 전체 통과 (2026-02-26)

식약처 테스트 시나리오 엑셀 기반, **의뢰→시료→결과→결재→성적서** 전체 흐름 검증 완료.

| 단계 | 서비스 | 설명 | 결과 | 핵심 데이터 |
|------|--------|------|------|-------------|
| 1 | `saveInspctReqest` | 의뢰등록 | ✅ | 임시번호: T0260100020 |
| 2 | `selectListInspctReqest` | 의뢰조회 | ✅ | 등록 확인 |
| 3 | `saveReqestSplore` | 시료등록 | ✅ | sploreSn=1, 3항목 |
| 4 | `selectListReqestSplore` | 시료조회 | ✅ | |
| 5 | `selectListReqestSploreExprIem` | 시험항목조회 | ✅ | 3건 (타르색소/대장균군/세균수) |
| 6 | `saveReqestSploreFee` | 수수료저장 | ✅ | 12,100원 |
| 7 | `saveInspctReqestRequst` | 의뢰요청 | ✅ | **정식번호: 260100059** |
| 10 | `saveSploreChargerAsign` | 접수배정 | ✅ | apitest34 배정 |
| 11 | `insertExprDiary` | 시험일지 | ✅ | exprDiarySn=24160551 |
| 16 | `saveSploreInspctResult` | 결과입력 | ✅ | 불검출/음성 |
| 21 | `saveSploreSanctnRecom` | 결재상신 | ✅ | |
| 28 | `saveSploreSanctn` | 최종결재 | ✅ | 1건 완료/총 1건 |
| 29 | `saveGrdcrtIssu` | 성적서발급 | ✅ | IM27000001/IM42000001 |
| 30 | `selectGrdcrtDmOutpt` | DM출력 | ✅ | DM_ADRESS_260100059.pdf (23KB) |
| 31 | `selectGrdcrtPdfOutpt` | PDF출력 | ⚠️ | 파일 다운로드 형식 (빈 JSON) |

**31단계 테스트 중 발견된 주요 사항:**

| 항목 | 내용 |
|------|------|
| `inspctInsttCntcValue` | 가이드 미수록 필수필드, reqestInfo에 포함 필요 (max 60자) |
| 품목코드 형식 | 2018년 `C01xxxxx` 형식 무효 → 현재 `A01xxxxx` 형식 사용 |
| `feeSeCode` | `IM26000004`(개별) 사용, `IM26000001`(그룹)은 feeGroupSn 필요 |
| `sploreChargerId` | `mfdsLimsId` 형식(apitest34) 사용, codeNo(L0330159) 불가 |
| `fdqntLimitApplcAt` | 결과입력 시 각 항목에 `"N"` 필수 |
| `jobSeCode` | 대부분의 write 서비스에 `"IM18000001"` 필수 |
| `prductNm` | 시료등록 시 제품명 필수 (가이드에 비중 낮게 표기됨) |

**미들웨어 URL 수정 (2026-02-26):**
- **문제**: `WebApiController.selectUnitTest()`가 서비스명만 AuthenticateCert에 전달 → `HttpPost("saveXxx")` → "Target host is not specified"
- **원인**: 원본 JSP 페이지에서는 `wslimsUrl + "/webService/rest/" + serviceName`으로 전체 URL 조합 후 전달했으나, `selectUnitTest`에는 이 로직이 없었음
- **해결**: `WebApiController.java`에 `buildRestUrl()` 메서드 추가, `url`이 `http`로 시작하지 않으면 자동으로 `wslimsUrl + "/webService/rest/"` 프리픽스 추가
- **파일**: `/home/biofl/tomcat/webapps/LMS_CLIENT_API/WEB-INF/classes/gov/mfds/lms_client/Controller/WebApiController.class` (Java 17 컴파일)

### ⏳ 다음 작업 (우선순위, 2026-03-01 갱신)

**1순위 — 관리자 > API 수집 검증:**
- `admin_api_settings.html` — API 수집 설정 페이지 검증
- `admin_collect_status.html` — 수집 현황 페이지 검증
- `api_server.py` (Flask port 5003) — 데이터 수집 서버 검증
- `collector.py` — 식약처 데이터 수집기 검증

**2순위 — 시험일지 양식 검토 (차주 예정):**
- 시험일지 양식 뷰어 (API 0241→0242) 실무 활용 검토
- 양식 편집 → 시험일지 등록(0209) 연동 완성
- 계산식(nomfrmCn) 구현: API에서 제공하는 계산식 데이터만 사용 (인터넷 검색 금지)

**3순위 — 접수등록 ↔ 식약처 의뢰 연동:**
- `sampleReceipt.html`에서 접수 저장 시 식약처 `saveInspctReqest` API 동시 호출
- 의뢰번호(`sploreReqestNo`) 발급받아 Firestore `receipts`에 저장
- 시료 정보도 `saveReqestSplore` API로 동시 전송
- 오류 시 식약처 연동만 실패하고 BFL 접수는 정상 저장되도록 독립 처리

**4순위 — 검사결과 입력 ↔ 식약처 연동 보강:**
- ✅ 시험일지 등록 (`insertExprDiary`) — 기본 구현 완료
- ✅ 검사결과 전송 (`saveSploreInspctResult`) — 기본 구현 완료
- ⏳ 계산식 결과 등록 (`insertExprDiaryCalcFrmlaResult`) — API 0210, 래퍼만 존재
- ⏳ 결재상신 (`saveSploreSanctnRecom`) — 미구현
- BFL 항목명 → 식약처 시험항목코드 매핑 활용 (`mfds_item_mappings`)

**5순위 — 성적서 발급 연동:**
- 성적서 발급 (`saveGrdcrtIssu`)
- 성적서 이력 조회 (`selectListGrdcrtIssuHist`)
- PDF 다운로드 연동

**6순위 — 운영 환경 전환:**
- 테스트(O000170) → 운영(O000026) 인증서/기관코드 전환
- `mfds-api.js`의 `DEFAULT_USER` 설정 변경
- application.properties 인증서 경로 변경
- 운영 MAC 등록 요청 (식약처)

### 식약처 연동 담당자 정보
| 구분 | 이름 | 연락처 | 비고 |
|------|------|--------|------|
| 통합LIMS 담당 | 이누리 대리 | - | MAC 재등록, webApi:Y 안내 |
| 운영·관리 | jhk0821@korea.kr | 043-234-3100 | 정보화도움터 |

### 트러블슈팅 기록
| 문제 | 원인 | 해결 | 상태 |
|------|------|------|------|
| `NoClassDefFoundError: javax.activation` | Java 17에서 모듈 제거됨 | `javax.activation-1.2.0.jar` 추가 | ✅ |
| Tomcat 포트 충돌 | 기존 Tomcat 이미 실행 중 | 중복 설치 삭제, 기존 인스턴스 활용 | ✅ |
| WAR에 JSP 없음 | 중간모듈 전용 빌드 | 정상 — API 호출만 제공 | ✅ |
| MAC 미감지 (`data`에 MAC 없음) | `/etc/hosts`가 hostname→127.0.1.1 매핑, `getLocalHost()`→loopback→NI null | `clientEthName=enp4s0` 설정 + WebApiController 5파라미터 생성자 | ✅ |
| `classes/` vs `config/` 혼동 | ResourceBundle은 `classes/`에서 읽음, Spring은 `config/`에서 읽음 | 두 파일 모두 설정 통일 | ✅ |
| **유효하지 않는 인증정보** | MAC 등록 형식 오류(`:` → `-`) + `webApi:"Y"` 미전송 | 이누리 대리 MAC 재등록 + `mfds-api.js`에 `webApi:"Y"` 추가 | ✅ |
| **한글 깨짐 (API 응답)** | Spring MVC 기본 인코딩이 ISO-8859-1 | `servlet-context.xml`에 `StringHttpMessageConverter` UTF-8 추가 | ✅ |
| **Test 3 부서목록 `-` 표시** | 필드명 불일치 (`deptCode`→`codeNo`, `deptName`→`codeName`) | `mfdsTest.html` 필드명 수정 | ✅ |
| **Test 4 직원목록 실패** | 서비스명 오류(`selectListUser`→`selectListEmp`) + `deptCode` 필수 누락 | 서비스명/파라미터 수정 | ✅ |
| **Test 5 품목분류 실패** | `jobRealmCode` 필수 파라미터 누락 | `jobRealmCode: 'IM36000001'` 추가 | ✅ |
| **Tomcat 재시작 실패** | shutdown.sh 후 기존 프로세스가 남아 8080 포트 점유 | 프로세스 완전 종료 대기 후 startup.sh | ✅ |
| **API 호출 빈 응답 (Content-Length:0)** | `selectUnitTest`가 서비스명만 전달 → `HttpPost("saveXxx")` 호스트 없음 | `WebApiController.buildRestUrl()` 추가, `wslimsUrl + "/webService/rest/"` 자동 프리픽스 | ✅ |
| **Step 3 시료등록 품목코드 오류** | 2018년 테스트코드(`C0113010000000`) 무효 | `A0100100000000` (쌀) 사용 | ✅ |
| **Step 10 접수배정 사용자ID 오류** | `codeNo`(L0330159) 대신 `mfdsLimsId`(apitest34) 사용해야 함 | ID 형식 변경 | ✅ |

### 식약처 연동 구현 현황 상세 (2026-03-01 기준)

#### JS 모듈 구성

| # | 파일 | 줄수 | 역할 | 의존성 |
|---|------|------|------|--------|
| 1 | `js/mfds-api.js` | 634 | API 호출 코어 (26개 래퍼 함수) | Firebase, nginx |
| 2 | `js/mfds-codes.js` | 652 | 코드매핑 로딩/캐싱/검색 | Firebase |
| 3 | `js/mfds_result_rules.js` | 157 | 결과값 처리 규칙 (유효자리수/정량한계/판정코드) | — |
| 4 | `js/mfds_templates.js` | 74,903 | 식약처 시험항목 템플릿 데이터 (646템플릿) | — |
| 5 | `js/mfds_diary_form.js` | 198 | 시험일지 양식 뷰어 (API 0241→0242) | mfds-api.js |
| 6 | `js/mfds-fee-mapping.js` | 178 | 수수료 매핑 데이터 | — |
| 7 | `js/food_types_qc.js` | 1,031 | 식품유형 품질관리 | — |
| 8 | `js/food_item_fee_mapping.js` | 9,261 | 식품항목-수수료 매핑 (9,237건) | — |

#### API 래퍼 함수 현황 (`mfds-api.js`)

| 분류 | 서비스ID | 래퍼 함수 | 실제 호출 여부 |
|------|---------|----------|:---:|
| **의뢰관리** | 0101 | `selectListInspctReqest` | ✅ |
| | 0104 | `saveInspctReqest` | ✅ (31단계 테스트) |
| | 0105 | `saveInspctReqestRequst` | ✅ (31단계 테스트) |
| | 0106 | `selectListReqestSplore` | ✅ (31단계 테스트) |
| | 0107 | `saveReqestSplore` | ✅ (31단계 테스트) |
| | 0108 | `selectListReqestSploreExprIem` | ✅ (31단계 테스트) |
| | 0109 | `saveReqestSploreFee` | ✅ (31단계 테스트) |
| | 0115 | `saveSploreChargerAsign` | ✅ (31단계 테스트) |
| **시험/결과** | 0202 | `selectListExprDiaryByExprIemSn` | ⏳ 래퍼만 |
| | 0206 | `selectListExprDiary` | ⏳ 래퍼만 |
| | 0207 | `selectExprDiaryDtl` | ⏳ 래퍼만 |
| | 0208 | `deleteExprDiary` | ⏳ 래퍼만 |
| | 0209 | `insertExprDiaryNew` | ✅ (testResultInput) |
| | 0210 | `insertExprDiaryCalcFrmlaResult` | ⏳ 래퍼만 |
| | 0216 | `saveSploreInspctResult` | ✅ (testResultInput) |
| | 0219 | `saveSploreSanctnRecom` | ⏳ 래퍼만 |
| | 0221 | `saveSploreSanctn` | ✅ (31단계 테스트) |
| | 0241 | `selectListExprMth` | ✅ (양식뷰어) |
| | 0242 | `selectListExprDiaryForm` | ✅ (양식뷰어) |
| **성적서** | 0309 | `saveGrdcrtIssu` | ✅ (31단계 테스트) |
| | 0310 | `selectListGrdcrtIssuHist` | ⏳ 래퍼만 |
| | 0311 | `selectGrdcrtDmOutpt` | ✅ (31단계 테스트) |
| | 0312 | `selectGrdcrtPdfOutpt` | ✅ (31단계 테스트) |
| **기관/사용자** | 0601 | `selectListDept` | ✅ |
| | 0602 | `selectListEmp` | ✅ |
| **공통** | 0801 | `selectListCmmnCode` | ✅ |
| | 0818 | `selectListPrdlstLclas` | ✅ |

> **26개 래퍼 중 19개 실제 호출 확인**, 7개는 래퍼만 존재 (향후 UI 연동 예정)

#### Firestore 컬렉션 (식약처 관련)

| 컬렉션 | 건수 | 용도 | 출처 |
|--------|------|------|------|
| `mfds_common_codes` | 383 | 공통코드 (IM15, IM16, IM17, IM35, IM43 등) | 코드매핑 Excel |
| `mfds_product_codes` | 8,404 | 품목코드 3단 계층 (대→중→소분류) | 코드매핑 Excel |
| `mfds_test_items` | 2,940 | 시험항목 코드/명칭/단위 | 코드매핑 Excel |
| `mfds_units` | 106 | 단위코드 (mg/kg, g/100g 등) | 코드매핑 Excel |
| `mfds_item_mappings` | 가변 | BFL↔식약처 항목 매핑 | 사용자 설정 |
| `mfds_cache` | 가변 | API 응답 캐시 (24시간 TTL) | API 자동생성 |
| `mfdsTemplates` | 2,657 | 식품유형별 시험항목 템플릿 | 코드매핑 XLS |
| `testResults` | 가변 | 검사결과 데이터 (calcData 포함) | 사용자 입력 |

#### 데이터 흐름도

```
[접수등록 sampleReceipt.html]
  ├→ 식약처 품목코드 선택 (mfds_product_codes 3단 드롭다운)
  ├→ 식품유형 선택 → mfdsTemplates에서 시험항목 자동 로드
  ├→ BFL↔식약처 항목 매핑 (mfds_item_mappings)
  └→ Firestore receipts 저장 (mfdsProductCode 포함)

[검사결과 입력 testResultInput.html]
  ├→ receipts 로드 → 시료별 시험항목 렌더링
  ├→ 측정값 입력 → MFDS_RULES 자동 적용
  │   ├→ 유효자리수 (validCphr, precision별 toFixed)
  │   ├→ 정량한계 (fdqntLimit, 미만시 불검출)
  │   └→ 표기값 (markValue) 생성
  ├→ 자동판정 (적합/부적합, maxValue/minValue 기준)
  ├→ Firestore testResults 저장
  ├→ [양식] 버튼 → API 0241→0242 체인 → 시험일지 HTML 양식 표시
  └→ 식약처 전송
      ├→ Step 1: insertExprDiaryNew (0209) → exprDiarySn 발급
      └→ Step 2: saveSploreInspctResult (0216) → 결과 전송
```

### 포트 사용 현황
| 포트 | 서비스 | 비고 |
|------|--------|------|
| 8080 | Tomcat (중간모듈) | 내부 전용 |
| 8443 | nginx SSL (BFL LIMS) | 외부 접근 |
| 5001 | 시료접수 API | Flask |
| 5002 | OCR 프록시 | Flask |
| 5003 | 식약처 데이터 API | Flask |

**⛔ 사용 금지 포트**: `443, 2222, 5000, 5050, 6001, 6005, 6800, 7000, 8000, 8443, 8501, 63964`

### 식약처 통합LIMS 수령 파일 패키지 (mfds_integration/)

**수령일**: 2026-02-25
**출처**: 식약처 통합LIMS 운영팀 (정보화도움터 043-234-3100)
**목적**: 통합LIMS WEB API 연동 개발용 자료 일체
**비고**: Git 미추적 (로컬 전용, `.gitignore` 대상 아님 — 인증서 포함으로 커밋 금지)

#### 파일 목록 (2026-02-25 일괄 수령)

| # | 파일/폴더 | 설명 | 비고 |
|---|----------|------|------|
| 1 | `(먼저읽어주세요)_개발테스트절차 및 주의사항.pdf` | 개발테스트 신청양식, MAC 등록 절차 | |
| 2 | `통합LIMS_WEB_API_검사기관개발가이드_V1.1.pdf` | 핵심 개발가이드 (19p) | API 연동 필독 |
| 3 | `통합LIMS_WEB_API_검사기관개발가이드_개정이력.pdf` | 가이드 변경 이력 | |
| 4 | `통합LIMS_WEB_API_테스트시나리오.xls` | 31단계 테스트 시나리오 | ✅ 전체 통과 (2026-02-26) |
| 5 | `통합테스트시나리오_자체의뢰 일반배정 시료별 결재상신.xls` | 자체의뢰 흐름 시나리오 | |
| 6 | `검사기관별_테스트계정_20260225.xlsx` | 테스트 계정 목록 (apitest01~40) | 바이오푸드랩: **apitest34** |
| 7 | `식약처 안내 메일.txt` | MAC 등록 안내, 임시비밀번호 | |
| 8 | `O000170.jks` | 테스트 기관 인증서 (비밀번호: mfds2015) | ⚠️ 커밋 금지 |
| 9 | `O000026.jks` | 운영 기관 인증서 (바이오푸드랩) | ⚠️ 커밋 금지 |
| 10 | `Sample/` | 클라이언트 API 샘플 (Java 소스) | WebApiController, WebApiService |
| 11 | `Sample_중간모듈/` | 중간모듈 WAR (62MB) + 샘플 | LMS_CLIENT_API.war |
| 12 | `서비스별 가이드/` | 167개 API 서비스별 PDF 가이드 | I-LMS-0101 ~ I-LMS-0818 |
| 13 | `DirectApiTest.java` | 독립 API 테스트 (WAR 우회) | 2026-02-26 작성 |
| 14 | `MacTest.java` | MAC 주소 감지 테스트 | 2026-02-26 작성 |

#### 코드매핑자료 (13개 Excel, 2026-02-25 수령)

식약처가 제공하는 **식품 분야(IM36000001) 코드 레퍼런스 데이터**. 검사기관이 통합LIMS 연동 시 사용할 품목/시험항목/기준규격 등의 표준 코드 체계.

| # | 파일 | 건수 | JSON 변환 | Firestore 컬렉션 | 현재 활용 |
|---|------|------|:---------:|-----------------|----------|
| 1 | `공통코드.xlsx` | 383건 | ✅ `common_codes.json` | `mfds_common_codes` | 드롭다운 코드 |
| 2 | `품목코드.xlsx` | 8,404건 | ✅ `product_codes.json` | `mfds_product_codes` | 접수등록 품목 선택 |
| 3 | `시험항목.xlsx` | 2,940건 | ✅ `test_items.json` | `mfds_test_items` | 검사항목 매핑 |
| 4 | `단위.xlsx` | 106건 | ✅ `units.json` | `mfds_units` | 단위 선택 |
| 5 | `기준_개별기준규격.xlsx` | ~15,993건 | ❌ 미변환 | — | 미활용 |
| 6 | `기준_공통기준규격.xlsx` | ~33,739건 | ❌ 미변환 | — | 미활용 |
| 7 | `기준_공통기준규격종류.xlsx` | ~11건 | ❌ 미변환 | — | 미활용 |
| 8 | `기준_개별기준상세규격.xlsx` | — | ❌ 미변환 | — | 미활용 |
| 9 | `기준_공통기준상세규격.xlsx` | — | ❌ 미변환 | — | 미활용 |
| 10 | `기준_단서조항.xlsx` | — | ❌ 미변환 | — | 미활용 |
| 11 | `품목속성.xlsx` | — | ❌ 미변환 | — | 미활용 |
| 12 | `부서_사용자목록.xlsx` | 5부서 16명 | ❌ 미변환 | — | 미활용 (테스트용) |
| 13 | `의뢰업체담당자목록.xlsx` | — | ❌ 미변환 | — | 미활용 |

**JSON 변환 경로**: `data/mfds/*.json` (2026-02-26 변환, 커밋 `4b69594`)
**업로드 도구**: `mfdsCodeUpload.html` (브라우저에서 Firestore 배치 업로드)

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

---

## 변경 이력

### 2026-02-27~28 (식약처 결과입력 구현)

#### 검사결과 입력 (`testResultInput.html`) — 전면 신규 구현
- **커밋**: `20367e4` ~ `99ff5ce` (8개 커밋)
- 접수현황에서 접수건 선택 → 시료별 시험항목 테이블 렌더링
- 측정값 입력 → `MFDS_RULES` 자동 적용 (유효자리수, 정량한계, 표기값)
- 자동판정: 최대값/최소값 기준 비교 (적합/부적합/검출/불검출)
- Firestore `testResults` 저장/복원
- 식약처 전송: 시험일지 등록(0209) + 결과 전송(0216) 2단계
- 시험일지 양식 뷰어: [양식] 버튼 → API 0241→0242 체인 → HTML 양식 표시
- **운영 서버 검증**: 납(B10001) 양식 "중금속_납_일지 [개인]" 정상 조회 확인

#### 식약처 결과값 처리 규칙 (`js/mfds_result_rules.js`)
- **커밋**: `a9e2c7e`
- 유효자리수(validCphr), 정량한계(fdqntLimit), 표기값(markValue) 자동 처리
- 판정형식(IM15), 판정용어(IM35), 최대값구분(IM16), 최소값구분(IM17) 코드 매핑

#### 시험일지 API 9개 래퍼 추가 (`js/mfds-api.js`)
- **커밋**: `5f602cb`
- 일지 조회(0202,0206,0207), 삭제(0208), 등록(0209), 계산식(0210), 결과전송(0216), 결재(0219,0221)

#### 시험일지 양식 뷰어 (`js/mfds_diary_form.js`)
- **커밋**: `99ff5ce`
- API 0241(시험방법) → 0242(양식조회) 체인
- 사용범위코드 3단계: 개인→부서→기관 우선순위 조회
- 빈 셀 contenteditable 변환, 편집 HTML 수집 기능

#### UI 개선
- **커밋**: `75d1724`, `4c01eba`, `74116f1`
- 사이드바 반응형 개선, 아코디언 섹션 디자인 통일
- 접수현황 선택 삭제 기능 수정 (`dc12c0c`)

#### 계산식(nomfrmCn) 구현 → Revert
- **커밋**: `b30c334` → **Revert**: `b4c6218`
- 인터넷 검색 기반 수식 직접 코딩 → 식약처 데이터 원칙 위반으로 전면 취소
- **교훈**: 계산식은 반드시 식약처 API(0210)에서 제공하는 데이터만 사용해야 함

### 2026-02-23

#### 검사관리 - 데이터 정리 (inspectionMgmt.html)
- **식품공전 탭 I2580 중첩 해결**: 식품유형(API)과 개별기준규격 탭이 동일 I2580 데이터를 중복 표시 → 식품공전 탭에서 개별기준규격 서브탭 제거, I2580은 식품유형(API)에서만 접근
- **공통기준규격(I2600) 반영**: 수집 중단된 I2600 데이터(31,000/56,716건)에 meta 문서 생성하여 UI 표시 가능하게 처리
- **식품유형 서브탭 3개 구성**: 식품유형(API) / 식품유형(커스텀) / 식품유형(맵핑)
- **식품유형(맵핑) 탭 신규**: Firestore `foodTypesMapping` 컬렉션, 식품/축산 라벨 필터 + 검사목적 필터, 카드/리스트 뷰

#### 접수등록 (sampleReceipt.html)
- **거래처 검색 인허가 기준 변경**: 인허가 필드(영업소명, 인허가번호, 업종, 주소) 검색 추가 (`firestore-helpers.js` 수정), 거래처명은 인허가 영업소명(licBizName) 우선 표시
- **시료번호 순번 부여**: 시료 수에 따라 접수번호-001, -002, -003 자동 부여 (`getSampleNo()` 수정)
- **검체유형 Firestore 연동**: 정적 JS(`js/full-food-types.js`) 의존 제거, Firestore `foodTypesMapping` 컬렉션에서 검체유형 로드
- **검사목적 + 시험분야 필터**: 선택한 검사목적(purpose)과 시험분야(식품/축산)에 해당하는 검체유형만 드롭다운에 표시

#### 접수현황 (receiptStatus.html)
- **시료별 행 분리**: 접수 1건(시료 N개) → N개 행으로 펼침 표시 (260700001-001, -002, -003)
- **상세모달 시료별 표시**: 클릭한 시료의 정보만 단독 표시 (기존: 모든 시료 일괄 표시)

#### Firestore 데이터
- `foodTypesMapping` 컬렉션 생성: `food_item_fee_mapping.js` 기반 9,237건 업로드 + 분야(식품/축산) 필드 추가
- **주의**: 현재 업로드된 맵핑 데이터는 재확인 필요 (올바른 자료가 아님, 추후 교체 예정)
- I2580 중복제거 적용: 16,104건 → 16,099건

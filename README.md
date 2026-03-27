# BioFoodLab LIMS

식품 시험 검사 기관을 위한 **통합 웹 기반 실험실 정보 관리 시스템** (Laboratory Information Management System)

**배포 (서버)**: https://14.7.14.31:8443/
**배포 (GitHub Pages)**: https://biofl1411.github.io/bfl_lims/

### 📁 문서 구조

| 문서 | 설명 |
|------|------|
| **[README.md](README.md)** | 프로그램 개요 (현재 문서) |
| **[README_FSS_API.md](README_FSS_API.md)** | 제조가공업소 API (식약처 공공 데이터 16개 API) |
| **[README_MFDS.md](README_MFDS.md)** | 식약처 통합LIMS WEB API 연동 |
| **[README_WORK_LOG.md](README_WORK_LOG.md)** | 작업 내용 (개발 이력 + 변경 이력) |
| **[NEXT_SESSION.md](NEXT_SESSION.md)** | 다음 세션 가이드 |
| **[BFL_LIMS_planning.md](BFL_LIMS_planning.md)** | 프로젝트 기획서 |
| **[SETUP_GUIDE.md](SETUP_GUIDE.md)** | API 서버 설치 가이드 |
| **WORK_LOG_*.md** | 날짜별 작업 일지 |

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
├── testDiary.html                     # 시험결재 > 시험일지 (MFDS API 연동)
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
| 4 | 시험 결재 | 9개 | 부분 구현 | `itemAssign.html`, `testResultInput.html`, `testDiary.html` |
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
  - **참고용 매핑**: 참고용(기준규격외) 시험항목별 수수료 (2,171건, 102건 설정), Firestore `settings/refFeeMapping`, 비고 컬럼 지원, **코드 접두사(A~X) 기반 10개 카테고리 분류 칩**, 500건 렌더 제한 성능 최적화, 코드 추가 모달(실시간 중복 검사), 분류 배지 컬럼
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

**사용하는 HTML 파일** (9개):
- `index.html`, `salesMgmt.html`, `companyRegForm_v2.html`, `sampleReceipt.html`, `itemAssign.html`, `testResultInput.html`, `testDiary.html`, `userMgmt.html`, `inspectionMgmt.html`, `adminSettings.html`

**메뉴 변경 시**: `js/sidebar.js`의 `SIDEBAR_MENU` 배열만 수정 → 8개 HTML 전체 자동 반영.

---

> **상세 문서**: [제조가공업소 API](README_FSS_API.md) | [식약처 통합LIMS 연동](README_MFDS.md) | [작업 내용](README_WORK_LOG.md)

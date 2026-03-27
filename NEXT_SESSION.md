# 새 대화 시작 시 읽어야 할 파일

## 필수 (항상 읽기)

| 파일 | 내용 | 이유 |
|------|------|------|
| `CLAUDE.md` | 프로젝트 설정, 절대 규칙, 식약처 데이터 원칙, 결과값 처리 규칙 | 모든 작업의 기본 규칙 |
| `NEXT_SESSION.md` | 이 파일 — 새 대화 컨텍스트 가이드 | 현재 상태 파악 |

## 최근 작업 이력 (작업 이어할 때)

| 날짜 | 주요 작업 |
|------|-----------|
| 2026-03-26 | **소분류 수수료 규칙 시스템** (공통 JS 모듈, 묶음 수수료 행, 접수등록+현황 통합) + **소분류 칩 추가** (E6/E7 잔류농약, FB/FC/FD 항생물질) + **시료별 독립 관리** (긴급/시험항목, Shift+클릭 연결) + **접수현황 개선** (긴급 이모지, sticky 가로 스크롤, 텍스트 복사) |
| 2026-03-25 | PA 507건/PB 299건 등록, 수수료 동시분석, 접수등록 개선, 소분류 관리 |
| 2026-03-24 | **접수 데이터 보호 전면 수정** + PA/PB 카테고리 + 소비기한 식품유형 임포트 + 참고용 수수료표 분석 (아래 상세) |
| 2026-03-23 | **접수등록 UI 전면 개편** + 지부관리 + 업체라벨 + 글꼴 설정 (아래 상세) |
| 2026-03-23(오전) | **P참고용 묶음(세트) 관리 시스템** — 4단계 계층 구현, 영양성분 자동 생성, 시험항목 탭 로딩 버그 수정 |
| 2026-03-20 | P참고용 소분류 구조 개편(P1/P2 순번→sub3 가로칩→sub4 세로묶음), 묶음 카드 CRUD, 결과단위 저장, 복사/이동/삭제 |
| 2026-03-19 | OCR 대폭 개선(Clova General+Claude 콜라보, 36개필드, 손글씨 보정 사전), 시험일지 연동, 소수점 다중 규칙, 결재 설정, 접수번호 중복방지, 수수료 부가세, 서버 안정화 |
| 2026-03-17(오후) | prefix 동기화 버그 수정, 하드코딩 제거, 기록서 양식 수집기 개선(시료유형 품목코드 매칭, 저장 후 다른 식품유형 적용 워크플로우) |
| 2026-03-17 | formCollector 파일명UI/시험법근거자동추출, 재고관리 코드매칭, **paymentMgmt 재구성 진행중(미완료)** |
| 2026-03-09 | 시험일지 전용 페이지 생성 (`testDiary.html`), mfds-api.js API 래퍼 3개 추가, sidebar 메뉴 추가 |
| 2026-03-06 | 서버 교체 복구 (nginx 설치, SSL 인증서, 권한 수정, 수집기 cron 복구) |
| 2026-03-05 | 보고번호 자동조회, 원재료 조회 버튼, 검사목적 항목 순서 정렬, 단위코드 검색 개선, 패키지 수수료, 검체유형 자연정렬 |
| 2026-03-04 | P코드 331종 생성, 한글명 우선순위, 수수료 필드, 데이터 손실 방지 (`WORK_LOG_20260304.md`) |
| 2026-03-01 | 수수료 Firestore 연동, 참고용 매핑 서브탭 (`WORK_LOG_20260301.md`) |

## 🔴 다음 세션 우선 작업 (2026-03-28)

### 1. 식약처 수집기 정밀 진단 + 수정 (최우선)
- **API별 수집 현황 > 신규 등록 업체 필드 삭제** (신규업체 목록 페이지 별도 존재)
- **API별 수집 현황 정렬 순서 관리자 설정** → 드래그 이동 + 순서대로 수집
- **변경 정보(I2859/I2860) 수집 중단 문제**: 3/15 이후 12일간 미수집, "이미 수집 완료" + "한도 초과로 건너뜀"
  - 원인: 수집 순서가 업소→품목→원재료→변경이력이라 변경이력은 항상 한도 부족
  - 해결: 수집 우선순위 조정 또는 변경이력 별도 수집
- **각 API별 정밀 진단**: 실제 수집 여부, 마지막 수집일, 오류 여부 확인
- **접수관리 > 설정 > "인허가 변경 정보" 페이지 신설**: fss_changes 데이터 조회/관리

### 2. 업무일지 잔여 작업
- 업무일지 저장 후 목록 표시 검증
- 상단 탭(미수금/거래명세표/계산서/세금계산서/차량일지) Firestore 연동
- 통계 카드 실시간 연동

---

## 🔴 기존 우선 작업 (2026-03-24)

### PA 참고용(식품) 시험항목 + 수수료 임포트
- **엑셀 원본**: `카카오톡 받은 파일/참고 검사항목 - 아이랩.xlsx` (507건, 중복 제거 477건)
- **검체유형**: 참고용검사(규격없음) 1종
- **수수료**: 부가세 포함 (5,500 ~ 385,000원)
- **단위**: 49종 (CFU/g, mg/kg, %, g/100g 등)
- **작업 내용**:
  1. 기존 P코드 항목과 이름 매칭 → 코드 할당 (매칭 안 되면 새 PA 코드 부여)
  2. PA 소분류에 477건 시험항목 등록 (Firestore mfdsTestItems)
  3. 수수료 매핑: 항목코드 → 수수료 (수수료 탭에서 관리)
  4. 같은 이름 다른 단위 항목 처리 (금속성이물 mg/kg vs ppm, 세균수 CFU/g vs CFU/mL)
  5. 소비기한 식품유형 임포트 시 PA 항목과 매칭
  6. (정량)/(정성) 구분 정확 매칭

### 소비기한 수수료 체계
- 소비기한 수수료표 별도 (참고용과 항목 공유, 수수료 다를 수 있음)
- 식품유형 × 항목 조합별 수수료 관리 필요
- 엑셀: `식품유형목록_20260324_053727.xlsx` (156건) → js/expiry-food-types.js 변환 완료

---

## 🔴 긴급 작업 목록 (2026-03-18 기준) — 다음 세션 최우선

### 0. 기록서 양식 → 시험일지/결과입력 연동 — **미착수, 최우선**

#### 0-1. 시험일지 반영 → 결과 입력 자동값 설정
- 시험 결재 > 시험 진행 현황 > 결과 입력에서 formTemplates 기반 입력 폼 생성 시, 자동으로 불러올 값 설정
- 현재 구조: `loadFormTemplates()` → `appliedToLims === true`인 템플릿 로드 → `renderCalcForm()` 으로 인라인 폼 생성
- **할 일**: 표준품 농도, 장비번호 등 반복 입력 필드를 사전 설정값으로 자동 채움
- 관련: `_formTemplatesCache`, `findFormTemplate()`, `renderCalcForm()`, `calcItemResult()`

#### 0-2. 시험일지에서 식품유형 선택/관리
- 시험 결재 > 시험 진행 현황 > 시험일지에서 해당 일지를 불러올 식품유형 선택 및 관리
- 현재: `diaryTemplates` 컬렉션에 항목코드별 양식 저장, `mfdsTemplates`에서 식품유형별 시험항목 매핑
- **할 일**: 일지 양식을 변경/수정할 때 해당 양식이 적용될 식품유형을 선택·관리하는 UI
- formTemplates(기록서 양식 수집기 저장 데이터)와 diaryTemplates(시험일지 양식) 연결

#### 0-3. 표준품 농도 등 입력값 관리
- 표준품 농도, 희석배수, 장비번호 등 반복 사용되는 입력값을 관리하는 기능
- analyzed.sections.fields 중 type이 number/text인 필드에 사전 설정값(preset) 저장
- Firestore에 저장하여 다음 입력 시 자동 채움

#### 참고: 현재 데이터 흐름
```
기록서 양식 수집 (formCollector)
  ↓ PDF 분석 → analyzed (sections, fields, calculations, judgmentRule)
  ↓ 검증완료 저장 → formTemplates 컬렉션
  ↓
결과 입력 (testResultInput)
  ↓ loadFormTemplates() → appliedToLims=true인 템플릿 로드
  ↓ renderCalcForm() → 인라인 계산 폼 생성
  ↓ calcItemResult() → 동적 계산 실행
  ↓
시험일지 (testDiary)
  ↓ diaryTemplates 컬렉션 → 항목별 일지 양식
  ↓ saveDiary() → 식약처 API 등록
  ↓ saveDiaryLocal() → Firestore testDiaries 저장
```

### 1. paymentMgmt.html 전면 재구성 — **미완료, 최우선**
- **현재 상태**: 기존 파일(1390줄) 분석 완료, 새 파일 작성 직전
- **목표**: 4탭 구조로 전면 재구성
  - **탭1 매출처 원장**: ledgerMgmt.html의 기능을 탭으로 통합 (서브탭: 원장+거래내역서), 이월행/매출행/입금행/합계행, KPI 4개, mfdsTemplates 검사항목 매칭
  - **탭2 입금 현황**: 기존 paymentMgmt.html의 입금 테이블+모달 그대로 유지 (탭 안으로 이동)
  - **탭3 은행 매칭**: 5단계 워크플로우(파일업로드→분석→유사도제안→입금반영→보고서), parseBankFile 개선(BANK_COL_MAP 헤더 자동탐지, 파일명 은행 감지, 주소 파싱), findBestMatch 5순위 매칭(학습DB 98%→업체명 90%→대표자 80%→주소 65%→미매칭), payment_depositors/payment_ambiguous/payment_reports 컬렉션 사용
  - **탭4 역추적 관리**: payment_ambiguous 목록, 역추적 4단계(주소→미수금범위→토큰분해→유사사례), 위험업체 등록
- **기존 JS 함수 모두 보존 필요** (목록):
  ```
  loadData(), loadCompanies(), loadMatchHistory(), saveMatchMapping()
  applyFilter(), renderTable(), updateSummary()
  getTotalFee(d), getPaidAmount(d), getPaymentStatus(d), getBadgeClass(), getPaymentMethods(), getLastPayDate()
  openModal(), closeModal(), processPayment(), deletePayment(), renderPayHistory()
  handleBankFiles(), parseBankFile(), parseBankDate(), parseAmt()
  renderBankTable(), clearBankData()
  autoMatchAll(), findAutoMatch(), cleanDepositorName()
  reverseTrack(), runReverseTrack(), renderTrackModal()
  selectTrackMatch(), searchManualMatch(), closeTrackModal(), unmatchDeposit()
  applySingleMatch(), applyAllMatches(), applySingleMatchSilent()
  formatDate(), formatMoney(), showToast()
  ```
- **ledgerMgmt.html에서 가져올 함수들**:
  ```
  switchSubTab(), _ledgerFmt(), _loadCompaniesCache(), _searchCompanies()
  _initAutocomplete(), _resolveCompanyAndFetch()
  loadLedger(), loadTxnStatement(), _loadMfdsTemplates(), _getTestItems()
  _buildTxnSummary(), _detectVatType(), _updateVatTag(), _methodTag()
  _getFee(), _getProductName(), _getDesc()
  _loadCompanyInfo(), _loadTxnCompanyInfo()
  exportTxnExcel(), printLedger(), printTxn()
  ```
- **참고 파일**: 기존 `paymentMgmt.html` (1390줄), `ledgerMgmt.html` (1149줄)

### 2. paymentStats.html 신규 생성 — paymentMgmt 완료 후 진행
- 4탭 구조: 결제나이(신호등 UI)/결제수단별/부서별/카드수수료
- 커밋 메시지: `feat: 입금통계 페이지 신규 생성 (신호등 UI, 결제주기/수단/부서/카드수수료)`

### 3. sidebar.js 수정 — paymentStats 완료 후 진행
- 재무관리 그룹에 `{ label: '입금 통계', page: 'finance-stats', href: 'paymentStats.html' }` 추가
- 위치: `js/sidebar.js` lines 166-170 사이

### 4. 커밋 + push + 서버 배포
- paymentMgmt: `git commit -m "feat: 입금관리 전면 재구성 - 원장/입금현황/은행매칭/역추적"`
- paymentStats: `git commit -m "feat: 입금통계 페이지 신규 생성"`
- `git push origin master:main`
- `ssh 192.168.0.96 → cd /home/biofl/bfl_lims && git pull origin main`

---

## 🔵 기존 작업 목록 (우선순위 낮음)

### 5. 접수등록 페이지 개선 (sampleReceipt.html) — 예정
- 보고번호 자동조회 + 검체유형 자동채움 (prdlst_dcnm → food-type)
- 원재료 조회 패널 UI 개선
- 기타 접수등록 UX 개선 사항

### 6. 업체조회 > 제품 원재료/변경사항 연결
- **위치**: salesMgmt.html `bizDetail()` 모달
- **현재**: 품목 + 변경이력 2탭만 존재
- **추가 필요**: 원재료 탭 (fss_materials 컬렉션 연결)
- `fss_materials` — C002(원재료 1,040,551건), C003(건강기능식품원재료 44,386건)

### 7. 참고용 영문명/체크 개선 (inspectionMgmt.html)
- 영문명 컬럼에 영문 화학명이 표시되지 않는 항목 수정
- testItemCode 없는 항목의 사용 체크박스 연동 완성

### 8. 식약처 통합LIMS 연동 (보류 중)
- MAC/인증서 등록 완료, API 연결 테스트 성공 확인 (2026-03-06)
- 31단계 테스트 시나리오 진행

## 주요 코드 파일 (기능별 필요 시)

### 접수 등록 (시료접수)
| 파일 | 핵심 내용 |
|------|-----------|
| `sampleReceipt.html` | 접수 등록 페이지 전체 (매우 큼, 필요한 부분만 읽기) |
| `js/mfds-codes.js` | 식약처 품목코드 피커, lockCategories, 시험항목 검색 |
| `js/mfds-fee-mapping.js` | 식약처 수수료 매핑 정적 데이터 166건 (JS 폴백용) |

### 검사 관리
| 파일 | 핵심 내용 |
|------|-----------|
| `inspectionMgmt.html` | 검사목적 관리 (검사분야, 목적, 품목코드, 식품유형, 시험항목, 기준규격, 참고용, 수수료) |

### 검사 결과 입력 / 시험일지
| 파일 | 핵심 내용 |
|------|-----------|
| `testResultInput.html` | 시험 결과 입력 + 식약처 전송 |
| `testDiary.html` | 시험일지 전용 페이지 (3패널 레이아웃, MFDS API 연동) |
| `js/mfds_result_rules.js` | MFDS_RULES — 유효자리수, 정량한계, 판정 처리 |
| `js/mfds_diary_form.js` | DIARY_FORM — 시험방법(0241)→양식(0242) 체인, 사용범위 3단계 |

### 식약처 연동
| 파일 | 핵심 내용 |
|------|-----------|
| `js/mfds-api.js` | 식약처 통합LIMS API 래퍼 (MFDS 객체) — 시험일지/시험항목/기준규격 포함 |
| `mfds_integration/서비스별 가이드/*.pdf` | API 스펙 원본 문서 |

### 사이드바 / 공통
| 파일 | 핵심 내용 |
|------|-----------|
| `js/sidebar.js` | SIDEBAR_MENU 정의 — 메뉴 변경 시 이것만 수정 |
| `js/firebase-init.js` | Firebase 초기화 |

## 현재 시스템 상태

### Firestore 주요 컬렉션
- `settings/mfdsFeeMapping` — 자가품질위탁검사용 수수료 (166건)
- `settings/refFeeMapping` — 참고용 수수료 (2,531건, P코드 331건 포함)
- `settings/inspectionPurposes` — 검사목적 P 배열
- `settings/inspectionFields` — 검사분야
- `inspectionFees` — 수수료 목록 전체 (7,481건)
- `mfds_test_items` — 식약처 시험항목 (~3,305건, P코드 331건 포함)
- `mfds_product_codes` — 식약처 품목코드 (7,849건)
- `mfdsTemplates` — 식약처 식품유형 템플릿 (646건)
- `itemGroups` — 참고용 항목 그룹 (2,791건, testItemCode 없음, 패키지수수료 필드 추가)
- `fss_products` — 식약처 품목 데이터 (1,043,170건) — 보고번호 자동조회용
- `fss_materials` — 식약처 원재료 데이터 (1,640,921건) — 원재료 조회용
- `fss_businesses` — 식약처 업소 데이터 (256,837건)
- `fss_changes` — 식약처 변경정보 (7건)

### 시험항목 코드 체계
- A: 이화학 (572) / B: 중금속 (966) / C: 미생물 (92) / D: 기생충 (6)
- E: 잔류농약 (769) / F: 동물용의약품 (229) / G: GMO (14)
- H: 이물/곰팡이 (17) / I: 질병검사 (18) / X: 기타 (291, RT-PCR/Elisa 포함)
- **P: 참고용 (331) — 임의지정 코드 (2026-03-04 신규)**

### 최근 구현된 기능 (2026-03-05~23)

#### P참고용 묶음(세트) 관리 (2026-03-20~23, inspectionMgmt.html)
- **4단계 계층 구조**: P소분류(P1) → sub3 가로칩(P1-01) → sub4 세로묶음(P1-01-1)
  - Firestore: `pRefSubCategories`, `pRefSub3Categories`, `pRefBundles` 3개 설정 문서
- **묶음 카드 기능**: 코드/이름 분리 표시, ↗이동, ⧉복사, ✕삭제, 더블클릭 이름수정, 드래그 순서변경
- **결과단위 필수**: `_pBundleUnits`에 항목별 단위 저장, 클릭 편집, Firestore 저장
- **영양성분 자동 생성**: P2-01(14대 g/mL 2세트), P2-02(9대 g/mL 2세트) — 패키지수수료 429,000원
- **클릭/더블클릭 분리**: 300ms 디바운스 + `_sub3DblFlag` 플래그
- **시험항목 탭 0건 버그 수정**: 탭 재방문 시 칩+필터+묶음패널 전체 재렌더링, CSS display 중복 수정
- **다음 세션 요청사항**:
  - 묶음 카드에서 코드(`P2-01-1`)와 이름(`14대 영양성분 (g)`)을 분리 표시 — 이미 구현됨
  - 복사(복붙) 기능 — 이미 구현됨 (⧉ 버튼)
  - 삭제 기능 — 이미 구현됨 (✕ 버튼)
  - 오작동 원인이 될 수 있는 잔존 캐시 정리 — nginx 캐시 삭제 완료, _mfdsTestLoaded 재렌더링 수정 완료
- **시험일지 전용 페이지** (`testDiary.html`): 3패널 레이아웃, MFDS API(0201/0202/0208/0209/0210/0211/0212/0241/0242/0243/0708/0113) 연동, 기준규격 선택 모달
- **보고번호 자동조회** (`sampleReceipt.html`): 인허가번호+제품명으로 `fss_products` 자동 매칭
- **원재료 조회 버튼** (`sampleReceipt.html`): 보고번호로 `fss_materials` 조회
- **검사목적 항목 순서 정렬** (`inspectionMgmt.html`): 숫자 입력으로 그룹 내 위치 변경
- **패키지 수수료** (`inspectionMgmt.html`): 영양성분 등 그룹 단위 패키지 가격 설정/표시/저장
- **단위코드 검색 개선** (`inspectionMgmt.html`): 전체 106건 표시, 슬래시/공백 무시 매칭
- **검체유형 자연정렬** (`inspectionMgmt.html`): `localeCompare` numeric으로 5일차 < 10일차

### Git
- Remote: `https://github.com/biofl1411/bfl_lims.git`
- 로컬 브랜치 `master` → 리모트 `main` (push: `git push origin master:main`)
- 새 컴퓨터에서 `git clone` 하면 `main` 브랜치로 통일됨

### 서버 (192.168.0.96) — 2026-03-06 교체 완료
- **OS**: Ubuntu, nginx 1.24.0 (2026-03-06 설치)
- **SSH**: paramiko 사용 (password: `bphsk*1411**`)
- **웹**: `https://192.168.0.96:8443/` (자체 서명 SSL, `/etc/nginx/ssl/`)
- **nginx 설정**: `/etc/nginx/sites-available/bfl_lims`
- **LIMS 루트**: `/home/biofl/bfl_lims` (chmod 755)
- **배포**: `ssh → cd /home/biofl/bfl_lims && git pull origin main`
- **서비스 자동시작**: `@reboot /home/biofl/start_services.sh`
- **식약처 수집기**: cron `0 18 * * *` (KST 03:00) `/home/biofl/fss_collector/collector.py --auto`
- **수집기 venv**: `/home/biofl/fss_collector/venv/bin/python` (python3.12 심볼릭 링크 복구됨)
- **포트**: 22(SSH), 5001~5003(Flask), 6001(경영실적), 7000(유통기한), 8080(tomcat), 8443(nginx), 8501(통계)

### 구 서버 (14.7.14.31)
- **SSH**: `ssh -p 2222 biofl@14.7.14.31` (pw: `bphsk*1411**`)

### Preview (로컬)
- port 8897 (`.claude/launch.json` → static-server)
- 5001(receipt_api), 5002(ocr_proxy), 5003(api_server)

### 포트 사용 금지
443, 2222, 5000, 5050, 6005, 6800, 8000, 63964

## 새 컴퓨터 설정 체크리스트

1. **Git clone**: `git clone https://github.com/biofl1411/bfl_lims.git`
2. **Python 패키지**: `pip install openpyxl paramiko`
3. **SSH 접속 테스트**: paramiko로 `192.168.0.96` 접속 확인
4. **배포 테스트**: `ssh → cd /home/biofl/bfl_lims && git status`

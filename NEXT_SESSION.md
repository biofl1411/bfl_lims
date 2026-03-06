# 새 대화 시작 시 읽어야 할 파일

## 필수 (항상 읽기)

| 파일 | 내용 | 이유 |
|------|------|------|
| `CLAUDE.md` | 프로젝트 설정, 절대 규칙, 식약처 데이터 원칙, 결과값 처리 규칙 | 모든 작업의 기본 규칙 |
| `NEXT_SESSION.md` | 이 파일 — 새 대화 컨텍스트 가이드 | 현재 상태 파악 |

## 최근 작업 이력 (작업 이어할 때)

| 날짜 | 주요 작업 |
|------|-----------|
| 2026-03-06 | 서버 교체 복구 (nginx 설치, SSL 인증서, 권한 수정, 수집기 cron 복구) |
| 2026-03-05 | 보고번호 자동조회, 원재료 조회 버튼, 검사목적 항목 순서 정렬, 단위코드 검색 개선, 패키지 수수료, 검체유형 자연정렬 |
| 2026-03-04 | P코드 331종 생성, 한글명 우선순위, 수수료 필드, 데이터 손실 방지 (`WORK_LOG_20260304.md`) |
| 2026-03-01 | 수수료 Firestore 연동, 참고용 매핑 서브탭 (`WORK_LOG_20260301.md`) |

## 🔵 다음 작업 목록 (2026-03-06 기준)

### 1. 접수등록 페이지 개선 (sampleReceipt.html) — 예정
- 보고번호 자동조회 + 검체유형 자동채움 (prdlst_dcnm → food-type)
- 원재료 조회 패널 UI 개선
- 기타 접수등록 UX 개선 사항

### 2. 업체조회 > 제품 원재료/변경사항 연결
- **위치**: salesMgmt.html `bizDetail()` 모달
- **현재**: 📦품목 + 📝변경이력 2탭만 존재
- **추가 필요**: 원재료 탭 (fss_materials 컬렉션 연결)
- `fss_materials` — C002(원재료 1,040,551건), C003(건강기능식품원재료 44,386건)

### 3. 참고용 영문명/체크 개선 (inspectionMgmt.html)
- 영문명 컬럼에 영문 화학명이 표시되지 않는 항목 수정
- testItemCode 없는 항목의 사용 체크박스 연동 완성

### 4. 식약처 통합LIMS 연동 (1순위 — 보류 중)
- MAC/인증서 등록 문제 해결 후 재개
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

### 검사 결과 입력
| 파일 | 핵심 내용 |
|------|-----------|
| `testResultInput.html` | 시험 결과 입력 + 식약처 전송 |
| `js/mfds_result_rules.js` | MFDS_RULES — 유효자리수, 정량한계, 판정 처리 |

### 식약처 연동
| 파일 | 핵심 내용 |
|------|-----------|
| `js/mfds-api.js` | 식약처 통합LIMS API 래퍼 (MFDS 객체) |
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

### 최근 구현된 기능 (2026-03-05~06)
- **보고번호 자동조회** (`sampleReceipt.html`): 인허가번호+제품명으로 `fss_products` 자동 매칭
- **원재료 조회 버튼** (`sampleReceipt.html`): 보고번호로 `fss_materials` 조회 (📋원재료 버튼)
- **검사목적 항목 순서 정렬** (`inspectionMgmt.html`): 숫자 입력으로 그룹 내 위치 변경
- **패키지 수수료** (`inspectionMgmt.html`): 영양성분 등 그룹 단위 패키지 가격 설정/표시/저장
- **단위코드 검색 개선** (`inspectionMgmt.html`): 전체 106건 표시, 슬래시/공백 무시 매칭
- **검체유형 자연정렬** (`inspectionMgmt.html`): `localeCompare` numeric으로 5일차 < 10일차

### Git
- Remote: `https://github.com/biofl1411/bfl_lims.git`
- ⚠️ 로컬 브랜치 `master` → 리모트 `main` (push: `git push origin master:main`)
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

## ⚠️ 새 컴퓨터 설정 체크리스트

1. **Git clone**: `git clone https://github.com/biofl1411/bfl_lims.git`
2. **Python 패키지**: `pip install openpyxl paramiko`
3. **SSH 접속 테스트**: paramiko로 `192.168.0.96` 접속 확인
4. **배포 테스트**: `ssh → cd /home/biofl/bfl_lims && git status`

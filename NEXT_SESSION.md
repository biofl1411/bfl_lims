# 새 대화 시작 시 읽어야 할 파일

## 필수 (항상 읽기)

| 파일 | 내용 | 이유 |
|------|------|------|
| `CLAUDE.md` | 프로젝트 설정, 절대 규칙, 식약처 데이터 원칙, 결과값 처리 규칙 | 모든 작업의 기본 규칙 |
| `NEXT_SESSION.md` | 이 파일 — 새 대화 컨텍스트 가이드 | 현재 상태 파악 |

## 최근 작업 이력 (작업 이어할 때)

| 파일 | 내용 |
|------|------|
| `WORK_LOG_20260301.md` | 2026-03-01 작업: 수수료 Firestore 연동, 참고용 매핑 서브탭 |

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
- `settings/refFeeMapping` — 참고용 수수료 (2,171건, 102건 설정됨)
- `settings/inspectionPurposes` — 검사목적 P 배열
- `settings/inspectionFields` — 검사분야
- `inspectionFees` — 수수료 목록 전체 (7,481건)
- `mfds_test_items` — 식약처 시험항목 (2,940건)
- `mfds_product_codes` — 식약처 품목코드 (7,849건)
- `mfdsTemplates` — 식약처 식품유형 템플릿 (646건)

### 배포
- **GitHub**: `git push origin main`
- **서버 SSH**: paramiko로 `14.7.14.31:2222` 접속 (user: biofl, pw: bphsk*1411**)
- **서버 배포**: `cd /home/biofl/bfl_lims && git pull origin main`
- **Preview 서버**: port 8897 (`.claude/launch.json` → static-server)

### 포트 사용 금지
443, 2222, 5000, 5050, 6001, 6005, 6800, 7000, 8000, 8443, 8501, 63964

### BFL Flask 포트
5001(시료접수), 5002(OCR), 5003(식약처)

# CLAUDE.md — BFL LIMS 프로젝트 설정

## 허용된 작업 (Allowed Operations)

### Bash 명령어
- 모든 터미널 명령어 실행 허용 (mkdir, rm, cp, mv, ls 등)
- npm, node, python, pip 등 패키지 관리자 실행
- git 전체 명령어 (add, commit, push, pull, fetch, branch, merge, rebase, stash, log, diff, status, clone, checkout, reset, tag)
- 스크립트 실행 (bash, sh, python, powershell)
- 파일 검색 및 시스템 명령어 (find, grep, rg, cat, head, tail, wc, sort, awk, sed)
- 서버 관련 명령어 (ssh, scp, curl, wget)
- 빌드/배포 명령어 (deploy.sh, deploy.ps1)

### 파일 읽기 (Read)
- 프로젝트 내 모든 파일 읽기 허용
- PDF 파일 읽기 허용 (mfds_integration/*.pdf 포함)
- 이미지 파일 읽기 허용 (png, jpg, svg 등)
- Excel/CSV 파일 읽기 허용
- JSON, JS, HTML, CSS, Python 등 모든 소스 파일
- .env, .gitignore, 설정 파일 등 모든 프로젝트 파일

### 파일 편집 (Edit/Write)
- 프로젝트 내 모든 파일 생성, 수정, 삭제 허용
- HTML, CSS, JS, Python 코드 변경
- 설정 파일 (json, yaml, properties 등) 수정
- README.md, CLAUDE.md 등 문서 파일 수정
- 새 파일 및 디렉토리 생성

### 웹 페치 (WebFetch)
- 모든 도메인 웹 페치 허용
- API 문서 및 레퍼런스 조회
- npm/CDN 패키지 정보 조회
- 식약처 공공 API 관련 문서 조회
- Firebase, Google Cloud 문서 조회
- GitHub 관련 정보 조회

### MCP 서버 (외부 서비스 연동)
- Claude in Chrome (브라우저 제어) 전체 허용
- Claude Preview (개발 서버 미리보기) 전체 허용
- MCP Registry (커넥터 검색/연결) 전체 허용
- 기타 연결 가능한 모든 MCP 도구 사용 허용

### 서버 배포 / GitHub 배포
- git push origin main 허용
- GitHub Pages 배포 허용
- SSH 서버 접속 허용 (ssh -p 2222 biofl@14.7.14.31)
- 서버 파일 동기화 (git pull on server)
- deploy.sh / deploy.ps1 스크립트 실행 허용
- gh CLI (GitHub CLI) 전체 명령어 허용

### 파일 접근
- 프로젝트 루트 및 하위 모든 디렉토리 접근 허용
- mfds_integration/ 폴더 (PDF, Excel, Java 소스 등) 접근 허용
- data/ 폴더 (GeoJSON, JSON 등) 접근 허용
- js/ 폴더 (모든 JavaScript 파일) 접근 허용
- etc/ 폴더 접근 허용
- .claude/ 폴더 접근 허용

---

## 프로젝트 개요

- **프로젝트**: BioFoodLab LIMS (식품 시험 검사 기관 실험실 정보 관리 시스템)
- **기술 스택**: Vanilla HTML/CSS/JS, Tailwind CSS, Firebase Firestore, Flask (Python)
- **배포**: GitHub Pages + Ubuntu 서버 (nginx 8443)
- **주요 문서**: README.md (전체 프로젝트 문서, 2,543줄)

## 주요 규칙

- 데이터는 반드시 Firebase Firestore에 저장 (localStorage는 보조/레거시)
- 사이드바 메뉴 변경 시 js/sidebar.js의 SIDEBAR_MENU만 수정
- firebase-ready 이벤트 이후 Firestore 접근
- 포트 사용 금지: 443, 2222, 5000, 5050, 6001, 6005, 6800, 7000, 8000, 8443, 8501, 63964
- BFL 내부 Flask 포트: 5001(시료접수), 5002(OCR), 5003(식약처)
- 커밋 시 한글 커밋 메시지 사용

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
// 결과값 전체 처리
var processed = MFDS_RULES.processResultValue(rawValue, item, judgmentResult);
// → { resultValue, markValue, validCphr, fdqntLimitApplcAt, jdgmntFomCode, jdgmntWordCode, ... }

// 개별 함수
MFDS_RULES.applyValidCphr(value, precision)     // 유효자리수 적용
MFDS_RULES.generateMarkValue(value, item)        // 표기값 생성
MFDS_RULES.mapJdgmntFomCode(judgmentType)        // IM15 코드 매핑
MFDS_RULES.mapJdgmntWordCode(judgmentResult)     // IM35 코드 매핑
```

### 데이터 소스
- 시험항목 템플릿: `js/mfds_templates.js` (precision, maxValue, maxValueCode, minValue, minValueCode 등)
- 공통코드: `data/mfds/common_codes.json` (IM15, IM16, IM17, IM35, IM43)
- API 스펙: `mfds_integration/서비스별 가이드/I-LMS-0216_시료검사결과+저장.pdf`

# CLAUDE.md — BFL LIMS 권한 및 배포 규칙

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

## 배포 정보

- **GitHub**: `git push origin main`
- **서버 SSH**: paramiko로 `14.7.14.31:2222` 접속 (user: biofl, pw: bphsk*1411**)
- **서버 배포**: `cd /home/biofl/bfl_lims && git pull origin main`
- **Preview 서버**: port 8897 (`.claude/launch.json` → static-server)
- **포트 사용 금지**: 443, 2222, 5000, 5050, 6001, 6005, 6800, 7000, 8000, 8443, 8501, 63964
- **BFL Flask 포트**: 5001(시료접수), 5002(OCR), 5003(식약처)
- **커밋 규칙**: 한글 커밋 메시지 사용

---

## 프로젝트 문서 참조

- **README.md**: 전체 프로젝트 문서 (기술 스택, 식약처 데이터 원칙, 결과값 처리 규칙, Firestore 구조, 커밋 이력 등)
- **NEXT_SESSION.md**: 새 대화 시작 시 읽어야 할 파일 가이드
- **WORK_LOG_*.md**: 작업 일지

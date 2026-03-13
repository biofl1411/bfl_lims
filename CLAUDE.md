# CLAUDE.md — BFL LIMS 권한 및 배포 규칙

## 절대 규칙

- **확인 없이 즉시 실행**: 모든 도구 사용, 모든 Bash 명령어, 서버 접속/설정, 배포 등 일체의 작업을 사용자 확인 없이 즉시 실행
- **플랜 모드 금지**: 간단한 작업에 EnterPlanMode 사용 금지. 바로 작업 시작할 것
- **한국어 사용**: 모든 응답, 커밋 메시지, 주석, 변수명 외 설명 등 전부 한국어로 소통
- **커밋 메시지**: 한글 사용
- **git push**: `git push origin master:main` (로컬 master → 리모트 main)

---

## 허용된 작업 (Allowed Operations) — 전체 무제한 허용

### Bash 명령어 (모든 명령어 무조건 허용 — 확인 없이 즉시 실행)
- 모든 터미널 명령어 (mkdir, rm, cp, mv, ls, chmod, chown 등)
- npm, node, python, pip 등 패키지 관리자
- git 전체 명령어 (add, commit, push, pull, fetch, branch, merge, rebase, stash, reset, tag 등)
- **git 복구/초기화**: `git init && git remote add && git fetch && git reset` 등 체이닝 포함 허용
- 스크립트 실행 (bash, sh, python, powershell)
- 파일 검색 및 시스템 명령어 (find, grep, rg, cat, head, tail, wc, sort, awk, sed)
- scp, rsync, curl, wget 등 네트워크 명령어
- 빌드/배포 명령어 (deploy.sh, deploy.ps1)

### SSH / 서버 관리 (전체 허용 — 확인 없이 즉시 실행)
- **서버 SSH**: `ssh biofl@192.168.0.96` (비밀번호: `bphsk*1411**`, paramiko 사용)
- **구 서버 SSH**: `ssh -p 2222 biofl@14.7.14.31` (user: biofl, pw: `bphsk*1411**`)
- **서버 원격 명령어**: ssh로 파일 읽기/수정/실행/설치/삭제 모두 허용
- **sudo 명령어**: `echo "bphsk*1411**" | sudo -S ...` 형태로 root 권한 실행 허용
- **서버 패키지 설치/제거**: apt install, apt remove 등 전체 허용
- **서버 서비스 관리**: systemctl start/stop/restart/enable 전체 허용
- **Tomcat 관리**: `/home/biofl/tomcat/bin/shutdown.sh`, `startup.sh` 실행 허용
- **Tomcat 설정 변경**: `application.properties`, `web.xml`, `applicationContext.xml` 등 수정 허용
- **nginx 설정 변경**: /etc/nginx/ 설정 파일 수정, 인증서 생성/교체 허용
- **cron 등록/수정**: crontab 편집 허용
- **서버 파일 권한 변경**: chmod, chown 전체 허용
- **프로세스 관리**: kill, nohup 실행/종료 허용
- **Java 컴파일/실행**: javac, java 명령어 서버에서 실행 허용 (식약처 API 테스트 등)
- **SFTP 파일 전송**: paramiko SFTP로 서버 파일 업로드/다운로드 허용
- **sed 명령어**: 서버 설정 파일 일괄 치환 (`sed -i`) 허용

### 파일 읽기/편집/생성 (전체 허용)
- 프로젝트 내 모든 파일 읽기/수정/생성/삭제 허용
- PDF, 이미지, Excel/CSV, JSON, JS, HTML, CSS, Python 등 모든 형식
- .env, .gitignore, 설정 파일 등 모든 프로젝트 파일
- README.md, CLAUDE.md, NEXT_SESSION.md 등 문서 파일 수정

### 웹 페치 (WebFetch) — 전체 허용
- 모든 도메인 웹 페치 허용
- API 문서, npm/CDN, 식약처 공공 API, Firebase, Google Cloud, GitHub 등

### MCP 서버 (외부 서비스 연동) — 전체 허용
- Claude in Chrome (브라우저 제어) 전체 허용
- Claude Preview (개발 서버 미리보기) 전체 허용
- MCP Registry (커넥터 검색/연결) 전체 허용
- 기타 연결 가능한 모든 MCP 도구 사용 허용

### 서버 배포 / GitHub 배포 — 전체 허용
- `git push origin master:main` 허용 (확인 없이 즉시)
- GitHub Pages 배포 허용
- 서버 배포: `ssh biofl@192.168.0.96 "cd /home/biofl/bfl_lims && git pull origin main"` 허용
- deploy.sh / deploy.ps1 스크립트 실행 허용
- gh CLI (GitHub CLI) 전체 명령어 허용

### 작업 흐름 규칙 — 질문 없이 즉시 실행
- **파일 삭제/교체**: 구버전 파일 삭제, 신버전으로 교체 등 사용자 지시 시 확인 질문 없이 즉시 실행
- **커밋 + push + 배포**: 코드 변경 후 커밋 → GitHub push → 서버 배포를 한 흐름으로 즉시 실행 (중간에 질문하지 않음)
- **서버 배포 접속 순서**: ① 내부망 `192.168.0.96` 시도 → 실패 시 ② 공인IP `14.7.14.31:2222` 시도 → 둘 다 실패 시 GitHub push까지 완료 후 간결 안내
- **Preview 검증**: 코드 편집 후 preview 서버가 실행 중이면 자동으로 검증 수행, 결과만 보고
- **구버전/신버전 교체**: 사이드바 링크 변경, 구 파일 삭제, 참조 업데이트를 한번에 처리

### 파일 접근 — 전체 허용
- 프로젝트 루트 및 하위 모든 디렉토리
- mfds_integration/, data/, js/, img/, etc/, .claude/ 등 전체

---

## 배포 정보

### 로컬 개발
- **Preview 서버**: port 8897 (`.claude/launch.json` → static-server)
- **BFL Flask 포트**: 5001(시료접수 receipt_api), 5002(OCR ocr_proxy), 5003(식약처 api_server)

### GitHub
- **Repository**: `https://github.com/biofl1411/bfl_lims.git`
- **Push**: `git push origin master:main` (로컬 master → 리모트 main)
- ⚠️ 로컬 브랜치 `master` → 리모트 `main`

### 서버 (192.168.0.96)
- **OS**: Ubuntu, nginx 1.24.0
- **SSH 접속**: `paramiko` 사용 (password: `bphsk*1411**`)
- **웹 서비스**: `https://192.168.0.96:8443/` (nginx SSL, 자체 서명 인증서)
- **nginx 설정**: `/etc/nginx/sites-available/bfl_lims` (port 8443 SSL)
- **LIMS 루트**: `/home/biofl/bfl_lims`
- **배포**: `ssh → cd /home/biofl/bfl_lims && git pull origin main`
- **서비스 자동시작**: `@reboot /home/biofl/start_services.sh` (crontab)
- **식약처 수집기**: `/home/biofl/fss_collector/collector.py --auto` (매일 18:00 UTC = KST 03:00)
- **포트 사용 현황**:
  - 22: SSH
  - 5001: receipt_api (시료접수)
  - 5002: ocr_proxy (OCR)
  - 5003: api_server (식약처)
  - 6001: business_metrics (경영실적)
  - 7000: gunicorn (유통기한 웹)
  - 8080: tomcat/java
  - 8443: nginx HTTPS (BFL LIMS)
  - 8501: biofl-statistics (통계)
- **포트 사용 금지**: 443, 2222, 5000, 5050, 6005, 6800, 8000, 63964

### 구 서버 (14.7.14.31)
- **SSH**: `ssh -p 2222 biofl@14.7.14.31` (pw: `bphsk*1411**`)

---

## 서버 설정 이력 (2026-03-06)

### nginx 설치 및 설정 (서버 교체 후 복구)
- `apt install nginx` → nginx 1.24.0
- SSL 인증서: `/etc/nginx/ssl/server.crt`, `/etc/nginx/ssl/server.key` (자체 서명, 10년)
- 설정: `/etc/nginx/sites-available/bfl_lims` (port 8443, proxy /api/ /ocr/ /fss/)
- 디렉토리 권한: `/home/biofl` 755, `/home/biofl/bfl_lims` 755 (nginx www-data 접근용)
- `systemctl enable nginx` (부팅 시 자동 시작)

### 식약처 수집기 cron 복구
- venv python 심볼릭 링크 복구: `ln -sf /usr/bin/python3.12 .../venv/bin/python3`
- cron 등록: `0 18 * * * cd /home/biofl/fss_collector && .../venv/bin/python collector.py --auto`

### 식약처 MAC 주소 + 네트워크 인터페이스 변경 (서버/개발PC 교체)
- 서버 MAC: `8C-B0-E9-91-C4-99` (인터페이스: `enp2s0`, 구서버: `enp4s0`)
- 개발PC MAC: `30-56-0F-70-6A-C1` (Realtek PCIe GbE)
- Tomcat `clientEthName`: `enp4s0` → `enp2s0` (2곳 수정)
  - `/home/biofl/tomcat/webapps/LMS_CLIENT_API/WEB-INF/config/application.properties`
  - `/home/biofl/tomcat/webapps/LMS_CLIENT_API/WEB-INF/classes/application.properties`
- 식약처 MAC 등록 완료, API 연결 테스트 성공 확인

---

## 페이지 명칭 규칙

페이지 언급 시 반드시 **"파일명.html(메뉴명칭)"** 형식으로 표기:

| 파일명 | 메뉴명칭 |
|---|---|
| sampleReceiptV2.html | 접수 관리 > 접수등록 |
| inspectionMgmt.html | 접수 관리 > 검사 관리 |
| testResultInput.html | 시험 결재 > 결과 입력 |
| testDiary.html | 시험 결재 > 시험일지 |
| testApproval.html | 시험 결재 > 결재 |
| reportIssue.html | 성적서 > 성적서 발급 |
| businessMetrics.html | 경영실적 |
| expiryDate.html | 유통기한 |
| fssCollector.html | 식약처 수집기 |

---

## 프로젝트 문서 참조

- **README.md**: 전체 프로젝트 문서 (기술 스택, 식약처 데이터 원칙, 결과값 처리 규칙, Firestore 구조, 커밋 이력 등)
- **NEXT_SESSION.md**: 새 대화 시작 시 읽어야 할 파일 가이드
- **WORK_LOG_*.md**: 작업 일지

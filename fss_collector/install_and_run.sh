#!/bin/bash
# ============================================================
# BioFoodLab 식약처 데이터 수집 시스템 - 원클릭 설치
# bioflsever에서 실행하세요
# ============================================================

set -e
echo ""
echo "=========================================="
echo " 식약처 데이터 수집 시스템 설치 시작"
echo "=========================================="
echo ""

# ─── 0. 설정 변수 ───
INSTALL_DIR="$HOME/fss_collector"
DB_NAME="fss_data"
DB_USER="fss_user"
DB_PASS="BioFL_fss_2026!"

# ─── 1. GitHub에서 최신 코드 가져오기 ───
echo "[1/7] GitHub 코드 가져오기..."
cd $HOME
if [ -d "bfl_lims" ]; then
  cd bfl_lims && git pull origin main
else
  git clone https://github.com/biofl1411/bfl_lims.git
  cd bfl_lims
fi
echo "  ✅ 코드 업데이트 완료"

# ─── 2. 설치 폴더 준비 ───
echo ""
echo "[2/7] 설치 폴더 준비..."
mkdir -p "$INSTALL_DIR/logs"
cp -f bfl_lims/fss_collector/* "$INSTALL_DIR/" 2>/dev/null || \
cp -f fss_collector/* "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/collector.py"
chmod +x "$INSTALL_DIR/api_server.py"
echo "  ✅ 파일 복사 완료: $INSTALL_DIR"

# ─── 3. Python 패키지 설치 ───
echo ""
echo "[3/7] Python 패키지 설치..."
pip3 install pymysql flask flask-cors --break-system-packages 2>/dev/null || \
pip3 install pymysql flask flask-cors 2>/dev/null || \
echo "  ⚠️ pip 설치 실패 - 수동 확인 필요"
echo "  ✅ 패키지 설치 완료"

# ─── 4. MariaDB 설정 ───
echo ""
echo "[4/7] MariaDB 데이터베이스 설정..."
echo "  MariaDB root 비밀번호를 입력하세요:"

mysql -u root -p -e "
CREATE DATABASE IF NOT EXISTS ${DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '${DB_USER}'@'localhost' IDENTIFIED BY '${DB_PASS}';
GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO '${DB_USER}'@'localhost';
FLUSH PRIVILEGES;
" 2>/dev/null

# 테이블 생성
mysql -u ${DB_USER} -p${DB_PASS} ${DB_NAME} < "$INSTALL_DIR/schema.sql" 2>/dev/null
echo "  ✅ DB 생성 완료 (${DB_NAME})"

# ─── 5. 환경변수 파일 ───
echo ""
echo "[5/7] 환경변수 설정..."
cat > "$INSTALL_DIR/.env" << ENVEOF
export FSS_DB_HOST=localhost
export FSS_DB_PORT=3306
export FSS_DB_USER=${DB_USER}
export FSS_DB_PASS=${DB_PASS}
export FSS_DB_NAME=${DB_NAME}
export FSS_API_KEY=e5a1d9f07d6c4424a757
export FSS_API_PORT=5050
ENVEOF
chmod 600 "$INSTALL_DIR/.env"
echo "  ✅ .env 파일 생성"

# ─── 6. Crontab 등록 (새벽 3시) ───
echo ""
echo "[6/7] Crontab 등록 (매일 03:00 KST)..."
CRON_LINE="0 3 * * * cd $INSTALL_DIR && source .env && /usr/bin/python3 collector.py >> logs/cron.log 2>&1"
(crontab -l 2>/dev/null | grep -v "collector.py"; echo "$CRON_LINE") | crontab -
echo "  ✅ Crontab 등록 완료"

# ─── 7. API 서버 시작 ───
echo ""
echo "[7/7] API 서버 시작..."

# 기존 프로세스 종료
pkill -f "python3.*api_server.py" 2>/dev/null || true
sleep 1

# 백그라운드 실행
cd "$INSTALL_DIR"
source .env
nohup python3 api_server.py > logs/api_server.log 2>&1 &
API_PID=$!
sleep 2

# 서버 확인
if kill -0 $API_PID 2>/dev/null; then
  echo "  ✅ API 서버 시작 (PID: $API_PID, 포트: 5050)"
else
  echo "  ⚠️ API 서버 시작 실패 - 로그 확인: $INSTALL_DIR/logs/api_server.log"
fi

echo ""
echo "=========================================="
echo " 설치 완료!"
echo "=========================================="
echo ""
echo " 📍 설치 경로: $INSTALL_DIR"
echo " 📍 DB: ${DB_NAME} (user: ${DB_USER})"
echo " 📍 API 서버: http://localhost:5050"
echo " 📍 관리자 페이지: http://localhost:5050/admin"
echo ""
echo "──────────────────────────────────────────"
echo " 이제 전체 데이터 수집을 시작합니다."
echo " 약 30~60분 소요됩니다."
echo " Ctrl+C로 중단 가능 (이어서 재실행 가능)"
echo "──────────────────────────────────────────"
echo ""
read -p "수집을 시작하시겠습니까? (Y/n): " CONFIRM
if [[ "$CONFIRM" != "n" && "$CONFIRM" != "N" ]]; then
  cd "$INSTALL_DIR"
  source .env
  python3 collector.py --full
else
  echo ""
  echo "나중에 수집하려면:"
  echo "  cd $INSTALL_DIR && source .env && python3 collector.py --full"
  echo ""
fi

#!/bin/bash
# ============================================================
# BioFoodLab 식약처 데이터 수집 시스템 설치
# bioflsever에서 실행
# ============================================================

set -e
echo "=========================================="
echo " 식약처 데이터 수집 시스템 설치"
echo "=========================================="

# ─── 0. 설정 ───
INSTALL_DIR="/home/biofl/fss_collector"
DB_NAME="fss_data"
DB_USER="fss_user"
DB_PASS="BioFL_fss_2026!"  # ← 실제 운영 시 변경하세요

echo ""
echo "[1/6] 파일 복사..."
mkdir -p "$INSTALL_DIR/logs"
cp collector.py api_server.py schema.sql "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/collector.py"
chmod +x "$INSTALL_DIR/api_server.py"

echo ""
echo "[2/6] Python 패키지 설치..."
pip3 install pymysql flask flask-cors --break-system-packages 2>/dev/null || \
pip3 install pymysql flask flask-cors

echo ""
echo "[3/6] MariaDB 데이터베이스 생성..."
echo "  (MariaDB root 비밀번호 입력이 필요할 수 있습니다)"
mysql -u root -p <<EOSQL
-- DB 생성
CREATE DATABASE IF NOT EXISTS ${DB_NAME}
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

-- 사용자 생성
CREATE USER IF NOT EXISTS '${DB_USER}'@'localhost' IDENTIFIED BY '${DB_PASS}';
GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO '${DB_USER}'@'localhost';
FLUSH PRIVILEGES;

-- 테이블 생성
USE ${DB_NAME};
SOURCE ${INSTALL_DIR}/schema.sql;
EOSQL

echo "  ✅ DB 생성 완료"

echo ""
echo "[4/6] 환경변수 설정..."
# .env 파일 생성
cat > "$INSTALL_DIR/.env" <<EOF
# 식약처 데이터 수집 시스템 환경변수
export FSS_DB_HOST=localhost
export FSS_DB_PORT=3306
export FSS_DB_USER=${DB_USER}
export FSS_DB_PASS=${DB_PASS}
export FSS_DB_NAME=${DB_NAME}
export FSS_API_KEY=e5a1d9f07d6c4424a757
export FSS_API_PORT=5050
EOF
chmod 600 "$INSTALL_DIR/.env"

echo "  ✅ 환경변수 파일 생성: $INSTALL_DIR/.env"

echo ""
echo "[5/6] Crontab 등록 (매일 새벽 3시 KST)..."
CRON_CMD="0 3 * * * cd $INSTALL_DIR && source .env && /usr/bin/python3 collector.py >> logs/cron.log 2>&1"

# 기존 crontab에 추가 (중복 방지)
(crontab -l 2>/dev/null | grep -v "collector.py"; echo "$CRON_CMD") | crontab -
echo "  ✅ Crontab 등록 완료"
echo "  확인: crontab -l"

echo ""
echo "[6/6] API 서버 systemd 등록..."
sudo tee /etc/systemd/system/fss-api.service > /dev/null <<EOF
[Unit]
Description=FSS Data API Server
After=network.target mariadb.service

[Service]
Type=simple
User=biofl
WorkingDirectory=$INSTALL_DIR
EnvironmentFile=$INSTALL_DIR/.env
ExecStart=/usr/bin/python3 api_server.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable fss-api
sudo systemctl start fss-api

echo "  ✅ API 서버 등록 완료 (포트 5050)"
echo ""
echo "=========================================="
echo " 설치 완료!"
echo "=========================================="
echo ""
echo " 다음 단계:"
echo ""
echo " 1. 전체 데이터 최초 수집 (약 30~60분 소요):"
echo "    cd $INSTALL_DIR"
echo "    source .env"
echo "    python3 collector.py --full"
echo ""
echo " 2. 수집 현황 확인:"
echo "    python3 collector.py --status"
echo ""
echo " 3. API 서버 확인:"
echo "    curl http://localhost:5050/api/status"
echo ""
echo " 4. 특정 API만 수집:"
echo "    python3 collector.py --full I1220 I2829"
echo ""
echo " 5. 매일 새벽 3시 자동 증분 수집 (cron 등록됨)"
echo ""

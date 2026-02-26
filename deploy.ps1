param($message = "Update")

Write-Host "`n===== BFL LIMS 배포 시작 =====" -ForegroundColor Cyan

# 1단계: Git commit & push
Write-Host "`n[1/3] Git commit & push..." -ForegroundColor Yellow
git add .
git commit -m $message
git push origin main

if ($LASTEXITCODE -ne 0) {
    Write-Host "Git push 실패!" -ForegroundColor Red
    exit 1
}
Write-Host "[1/3] Git push 완료" -ForegroundColor Green

# 2단계: 서버에 SSH로 git pull
Write-Host "`n[2/3] 서버(bioflsever) 배포 중..." -ForegroundColor Yellow
ssh biofl@192.168.0.96 "cd /home/biofl/bfl_lims && git pull origin main 2>&1"

if ($LASTEXITCODE -ne 0) {
    Write-Host "서버 배포 실패!" -ForegroundColor Red
    exit 1
}
Write-Host "[2/3] 서버 배포 완료" -ForegroundColor Green

# 3단계: 확인
Write-Host "`n[3/3] 배포 결과 확인..." -ForegroundColor Yellow
ssh biofl@192.168.0.96 "cd /home/biofl/bfl_lims && git log --oneline -1"

Write-Host "`n===== 배포 완료! =====" -ForegroundColor Green
Write-Host "  로컬: http://localhost:5500" -ForegroundColor White
Write-Host "  서버: http://192.168.0.96 (nginx)" -ForegroundColor White
Write-Host "  GitHub: https://biofl1411.github.io/bfl_lims/" -ForegroundColor White

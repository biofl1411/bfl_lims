param($message = "Update")
Write-Host " 배포 시작..." -ForegroundColor Cyan
git add .
git commit -m $message
git push origin main
Write-Host " 배포 완료!" -ForegroundColor Green
Write-Host " https://biofl1411.github.io/bfl_lims/" -ForegroundColor Yellow

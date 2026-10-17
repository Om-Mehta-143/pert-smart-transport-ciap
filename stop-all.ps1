Write-Host "Stopping PERT DevSecOps Platform containers..." -ForegroundColor Yellow
docker stop local-jenkins local-sonarqube 2>$null | Out-Null
Write-Host "Jenkins & SonarQube containers stopped." -ForegroundColor Green

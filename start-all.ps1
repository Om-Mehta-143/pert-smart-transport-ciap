Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  Starting PERT Smart Transport DevSecOps Platform...    " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Ensure Docker Desktop is Running
Write-Host "[1/3] Checking Docker Desktop..." -ForegroundColor Yellow
$dockerReady = $false
try {
    $null = docker info 2>$null
    if ($LASTEXITCODE -eq 0) { $dockerReady = $true }
} catch {
    $dockerReady = $false
}

if (-not $dockerReady) {
    Write-Host "      Starting Docker Desktop..." -ForegroundColor Magenta
    Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    Write-Host "      Waiting for Docker daemon to initialize..." -NoNewline
    while (-not $dockerReady) {
        Start-Sleep -Seconds 3
        Write-Host "." -NoNewline
        try {
            $null = docker info 2>$null
            if ($LASTEXITCODE -eq 0) { $dockerReady = $true }
        } catch {}
    }
    Write-Host " Ready!" -ForegroundColor Green
} else {
    Write-Host "      Docker is already running." -ForegroundColor Green
}

# 2. Start Jenkins & SonarQube Containers
Write-Host "[2/3] Starting Jenkins and SonarQube containers..." -ForegroundColor Yellow
docker start local-jenkins local-sonarqube 2>$null | Out-Null
Write-Host "      Jenkins (Port 8080)   -> UP" -ForegroundColor Green
Write-Host "      SonarQube (Port 9000) -> UP" -ForegroundColor Green

# 3. Check Flask Web App (Port 5000)
Write-Host "[3/3] Checking Flask Application (Port 5000)..." -ForegroundColor Yellow
$appRunning = $false
try {
    $resp = Invoke-WebRequest -Uri "http://localhost:5000" -Method Head -TimeoutSec 2 -ErrorAction SilentlyContinue
    if ($resp.StatusCode -eq 200) { $appRunning = $true }
} catch {}

if (-not $appRunning) {
    Write-Host "      Starting Flask App on port 5000..." -ForegroundColor Magenta
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; .\venv\Scripts\Activate.ps1; python .\app.py" -WindowStyle Minimized
    Start-Sleep -Seconds 2
    Write-Host "      Flask App             -> UP" -ForegroundColor Green
} else {
    Write-Host "      Flask App             -> ALREADY RUNNING" -ForegroundColor Green
}

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  ALL SYSTEMS READY & RUNNING!                            " -ForegroundColor Green
Write-Host "  - Web Application : http://localhost:5000               " -ForegroundColor White
Write-Host "  - Jenkins CI/CD   : http://localhost:8080               " -ForegroundColor White
Write-Host "  - SonarQube SAST  : http://localhost:9000               " -ForegroundColor White
Write-Host "  - Live AWS Cloud  : http://3.107.7.239:5000             " -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan

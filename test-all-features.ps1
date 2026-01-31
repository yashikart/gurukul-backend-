# Gurukul Feature Test Suite (PowerShell)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Gurukul Feature Test Suite" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if services are running
Write-Host "[1/4] Checking if services are running..." -ForegroundColor Yellow
try {
    $frontend = Invoke-WebRequest -Uri "http://localhost:5173" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
    Write-Host "✅ Frontend is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Frontend not running on port 5173" -ForegroundColor Red
    Write-Host "   Please run start-all.bat first!" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

try {
    $backend = Invoke-WebRequest -Uri "http://localhost:3000/health" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
    Write-Host "✅ Backend is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend not running on port 3000" -ForegroundColor Red
    Write-Host "   Please run start-all.bat first!" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Install dependencies
Write-Host "[2/4] Installing test dependencies..." -ForegroundColor Yellow
Set-Location "tests\e2e"

if (-not (Test-Path "node_modules")) {
    Write-Host "Installing npm packages..." -ForegroundColor Yellow
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    
    Write-Host "Installing Playwright browsers..." -ForegroundColor Yellow
    npx playwright install chromium
}

Write-Host "✅ Dependencies ready" -ForegroundColor Green
Write-Host ""

# Create test users
Write-Host "[3/4] Creating test users..." -ForegroundColor Yellow
python create-test-users.py
Write-Host ""

# Run tests
Write-Host "[4/4] Running E2E tests..." -ForegroundColor Yellow
Write-Host "This will test all features automatically..." -ForegroundColor Cyan
Write-Host ""
npm test

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Test Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "View detailed report:" -ForegroundColor Yellow
Write-Host "  cd tests\e2e" -ForegroundColor Gray
Write-Host "  npm run test:report" -ForegroundColor Gray
Write-Host ""
Read-Host "Press Enter to exit"


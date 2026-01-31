@echo off
echo ========================================
echo   Gurukul Feature Test Suite
echo ========================================
echo.

echo [1/4] Checking if services are running...
curl -s http://localhost:5173 >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Frontend not running on port 5173
    echo    Please run start-all.bat first!
    pause
    exit /b 1
)

curl -s http://localhost:3000/health >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Backend not running on port 3000
    echo    Please run start-all.bat first!
    pause
    exit /b 1
)

echo ✅ Services are running
echo.

echo [2/4] Installing test dependencies...
cd tests\e2e
if not exist node_modules (
    echo Installing npm packages...
    call npm install
    if %errorlevel% neq 0 (
        echo ❌ Failed to install dependencies
        pause
        exit /b 1
    )
    
    echo Installing Playwright browsers...
    call npx playwright install chromium
)

echo ✅ Dependencies ready
echo.

echo [3/4] Creating test users...
python create-test-users.py
echo.

echo [4/4] Running E2E tests...
echo This will test all features automatically...
echo.
call npm test

echo.
echo ========================================
echo   Test Complete!
echo ========================================
echo.
echo View detailed report:
echo   cd tests\e2e
echo   npm run test:report
echo.
pause


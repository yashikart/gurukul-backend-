@echo off
echo.
echo === Starting All Services ===
echo.
echo Opening 5 separate CMD windows...
echo.

REM Start Gurukul Backend
start "Gurukul Backend" cmd /k "cd /d %~dp0backend && echo Gurukul Backend starting on http://localhost:3000 && uvicorn app.main:app --host 0.0.0.0 --port 3000 --reload"

REM Wait a bit
timeout /t 1 /nobreak >nul

REM Start EMS Backend
start "EMS Backend" cmd /k "cd /d %~dp0EMS System && echo EMS Backend starting on http://localhost:8000 && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

REM Wait a bit
timeout /t 1 /nobreak >nul

REM Karma Tracker is now integrated into Gurukul Backend - no separate service needed!

REM Wait a bit
timeout /t 1 /nobreak >nul

REM Start Gurukul Frontend
start "Gurukul Frontend" cmd /k "cd /d %~dp0Frontend && echo Gurukul Frontend starting on http://localhost:5173 && npm run dev"

REM Wait a bit
timeout /t 1 /nobreak >nul

REM Start EMS Frontend
start "EMS Frontend" cmd /k "cd /d %~dp0EMS System\frontend && echo EMS Frontend starting on http://localhost:3001 && npm run dev"

REM Wait a bit
timeout /t 3 /nobreak >nul

REM Start Bucket Consumer (integrated mode - uses same backend for karma)
start "Bucket Consumer" cmd /k "cd /d %~dp0backend && echo Bucket Consumer starting (integrated mode)... && python scripts/start_bucket_consumer.py"

echo.
echo All services are starting in separate windows!
echo.
echo Service URLs:
echo   - Gurukul Backend:  http://localhost:3000 (includes Karma Tracker)
echo   - EMS Backend:      http://localhost:8000
echo   - Gurukul Frontend: http://localhost:5173
echo   - EMS Frontend:     http://localhost:3001
echo   - Bucket Consumer:  Processing PRANA packets (integrated mode)
echo.
pause


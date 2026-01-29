@echo off
echo.
echo === Starting All Services ===
echo.
echo Opening 4 separate CMD windows...
echo.

REM Start Gurukul Backend
start "Gurukul Backend" cmd /k "cd /d %~dp0backend && echo Gurukul Backend starting on http://localhost:3000 && uvicorn app.main:app --host 0.0.0.0 --port 3000 --reload"

REM Wait a bit
timeout /t 1 /nobreak >nul

REM Start EMS Backend
start "EMS Backend" cmd /k "cd /d %~dp0EMS System && echo EMS Backend starting on http://localhost:8000 && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

REM Wait a bit
timeout /t 1 /nobreak >nul

REM Start Karma Tracker
start "Karma Tracker" cmd /k "cd /d %~dp0Karma Tracker && echo Karma Tracker starting on http://localhost:8001 && call .venv\Scripts\activate.bat && uvicorn main:app --host 0.0.0.0 --port 8001 --reload"

REM Wait a bit
timeout /t 1 /nobreak >nul

REM Start Gurukul Frontend
start "Gurukul Frontend" cmd /k "cd /d %~dp0Frontend && echo Gurukul Frontend starting on http://localhost:5173 && npm run dev"

REM Wait a bit
timeout /t 1 /nobreak >nul

REM Start EMS Frontend
start "EMS Frontend" cmd /k "cd /d %~dp0EMS System\frontend && echo EMS Frontend starting on http://localhost:3001 && npm run dev"

echo.
echo All services are starting in separate windows!
echo.
echo Service URLs:
echo   - Gurukul Backend:  http://localhost:3000
echo   - EMS Backend:      http://localhost:8000
echo   - Karma Tracker:    http://localhost:8001
echo   - Gurukul Frontend: http://localhost:5173
echo   - EMS Frontend:     http://localhost:3001
echo.
pause


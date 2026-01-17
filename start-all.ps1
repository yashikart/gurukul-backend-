# Start All Services Script
# This script opens 4 separate PowerShell windows, one for each service

Write-Host "`n=== Starting All Services ===" -ForegroundColor Green
Write-Host "`nOpening 4 terminal windows..." -ForegroundColor Yellow

# Start Gurukul Backend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\backend'; Write-Host 'Gurukul Backend starting on http://localhost:3000' -ForegroundColor Cyan; uvicorn app.main:app --host 0.0.0.0 --port 3000 --reload"

# Wait a bit
Start-Sleep -Seconds 1

# Start EMS Backend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\EMS System'; Write-Host 'EMS Backend starting on http://localhost:8000' -ForegroundColor Cyan; uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

# Wait a bit
Start-Sleep -Seconds 1

# Start Gurukul Frontend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\Frontend'; Write-Host 'Gurukul Frontend starting on http://localhost:5173' -ForegroundColor Cyan; npm run dev"

# Wait a bit
Start-Sleep -Seconds 1

# Start EMS Frontend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\EMS System\frontend'; Write-Host 'EMS Frontend starting on http://localhost:3001' -ForegroundColor Cyan; npm run dev"

Write-Host "`n✅ All services are starting in separate windows!" -ForegroundColor Green
Write-Host "`nService URLs:" -ForegroundColor Yellow
Write-Host "  • Gurukul Backend:  http://localhost:3000" -ForegroundColor White
Write-Host "  • EMS Backend:      http://localhost:8000" -ForegroundColor White
Write-Host "  • Gurukul Frontend: http://localhost:5173" -ForegroundColor White
Write-Host "  • EMS Frontend:     http://localhost:3001" -ForegroundColor White
Write-Host "`nPress any key to exit this window (services will continue running)..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")


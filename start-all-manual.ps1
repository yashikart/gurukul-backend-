# Manual Start Script - Run each command in a separate PowerShell window
# Copy and paste each section into a new PowerShell terminal

Write-Host "=== MANUAL START INSTRUCTIONS ===" -ForegroundColor Yellow
Write-Host ""
Write-Host "Open 4 separate PowerShell windows and run these commands:" -ForegroundColor Cyan
Write-Host ""
Write-Host "WINDOW 1 - Gurukul Backend:" -ForegroundColor Green
Write-Host "cd backend" -ForegroundColor White
Write-Host "uvicorn app.main:app --host 0.0.0.0 --port 3000 --reload" -ForegroundColor White
Write-Host ""
Write-Host "WINDOW 2 - EMS Backend:" -ForegroundColor Green
Write-Host "cd 'EMS System'" -ForegroundColor White
Write-Host "uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload" -ForegroundColor White
Write-Host ""
Write-Host "WINDOW 3 - Gurukul Frontend:" -ForegroundColor Green
Write-Host "cd Frontend" -ForegroundColor White
Write-Host "npm run dev" -ForegroundColor White
Write-Host ""
Write-Host "WINDOW 4 - EMS Frontend:" -ForegroundColor Green
Write-Host "cd 'EMS System\frontend'" -ForegroundColor White
Write-Host "npm run dev" -ForegroundColor White
Write-Host ""
Write-Host "Press any key to open PowerShell windows automatically..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Try to open windows automatically
$scriptRoot = $PSScriptRoot
if (-not $scriptRoot) { $scriptRoot = Get-Location }

Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptRoot\backend'; Write-Host 'Gurukul Backend - http://localhost:3000' -ForegroundColor Cyan; uvicorn app.main:app --host 0.0.0.0 --port 3000 --reload"
Start-Sleep -Seconds 1
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptRoot\EMS System'; Write-Host 'EMS Backend - http://localhost:8000' -ForegroundColor Cyan; uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
Start-Sleep -Seconds 1
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptRoot\Frontend'; Write-Host 'Gurukul Frontend - http://localhost:5173' -ForegroundColor Cyan; npm run dev"
Start-Sleep -Seconds 1
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptRoot\EMS System\frontend'; Write-Host 'EMS Frontend - http://localhost:3001' -ForegroundColor Cyan; npm run dev"

Write-Host "`n✅ All services should be starting!" -ForegroundColor Green


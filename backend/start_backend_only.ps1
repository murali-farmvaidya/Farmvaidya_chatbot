# Start ONLY the backend (using external LightRAG)

Write-Host "=== Stopping All Services ===" -ForegroundColor Yellow

Get-Process | Where-Object {
    $ports = netstat -ano | Select-String $_.Id | Select-String "8000|9621"
    $ports.Count -gt 0
} | ForEach-Object {
    Write-Host "Stopping process $($_.Id) ($($_.ProcessName))" -ForegroundColor Gray
    Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
}

Write-Host "Services stopped." -ForegroundColor Green
Start-Sleep -Seconds 2

Write-Host ""
Write-Host "=== Starting Backend Only ===" -ForegroundColor Yellow
Write-Host "Using external LightRAG: https://convo-chatbot.onrender.com" -ForegroundColor Cyan

$env:PYTHONIOENCODING = "utf-8"
Set-Location "C:\Users\mural\Farm_Vaidya_Internship\chatbot\farmvaidya-conversational-ai\backend"

Write-Host ""
Write-Host "Starting uvicorn..." -ForegroundColor Gray
.\venv\Scripts\uvicorn.exe app.main:app --host 0.0.0.0 --port 8000 --reload

Write-Host ""
Write-Host "Backend stopped." -ForegroundColor Yellow

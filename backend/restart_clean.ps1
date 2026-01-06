# Clean restart - stops all services and clears LightRAG knowledge base

Write-Host "=== Stopping All Services ===" -ForegroundColor Yellow

# Stop all Python processes on our ports
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
Write-Host "=== Clearing LightRAG Knowledge Base ===" -ForegroundColor Yellow

$ragStorage = "C:\Users\mural\Farm_Vaidya_Internship\chatbot\farmvaidya-conversational-ai\backend\lightrag\Lightrag_main\rag_storage"

if (Test-Path $ragStorage) {
    Write-Host "Removing $ragStorage" -ForegroundColor Gray
    Remove-Item -Path $ragStorage -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "Knowledge base cleared." -ForegroundColor Green
} else {
    Write-Host "Knowledge base already empty." -ForegroundColor Green
}

Write-Host ""
Write-Host "=== Starting Services ===" -ForegroundColor Yellow
Write-Host "Run: python start_services.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "Note: Upload documents AFTER testing chat works!" -ForegroundColor Red

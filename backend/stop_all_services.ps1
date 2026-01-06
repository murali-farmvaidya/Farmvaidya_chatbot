# Stop all services (Backend + LightRAG)
# This script stops both the FastAPI backend and LightRAG server

Write-Host "========================================" -ForegroundColor Red
Write-Host "  Stopping Farm Vaidya Services" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Red
Write-Host ""

$ErrorActionPreference = "Continue"

# Function to kill processes on a specific port
function Stop-ProcessOnPort {
    param(
        [int]$Port,
        [string]$ServiceName
    )
    
    Write-Host "Stopping $ServiceName (port $Port)..." -ForegroundColor Yellow
    
    $connections = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    
    if ($connections) {
        foreach ($conn in $connections) {
            $processId = $conn.OwningProcess
            $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
            
            if ($process) {
                Write-Host "  - Stopping process: $($process.ProcessName) (PID: $processId)" -ForegroundColor Gray
                Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
            }
        }
        Write-Host "  ✓ $ServiceName stopped" -ForegroundColor Green
    } else {
        Write-Host "  - No process found on port $Port" -ForegroundColor Gray
    }
}

# Stop Backend (port 8000)
Stop-ProcessOnPort -Port 8000 -ServiceName "Backend Server"

# Stop LightRAG (port 9621)
Stop-ProcessOnPort -Port 9621 -ServiceName "LightRAG Server"

# Also stop any uvicorn or lightrag-server processes that might be running
Write-Host ""
Write-Host "Cleaning up remaining processes..." -ForegroundColor Yellow

$uvicornProcesses = Get-Process | Where-Object { $_.ProcessName -like "*uvicorn*" -or $_.CommandLine -like "*uvicorn*" } -ErrorAction SilentlyContinue
if ($uvicornProcesses) {
    $uvicornProcesses | ForEach-Object {
        Write-Host "  - Stopping uvicorn process (PID: $($_.Id))" -ForegroundColor Gray
        Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
    }
}

$lightragProcesses = Get-Process | Where-Object { $_.ProcessName -like "*lightrag*" -or $_.CommandLine -like "*lightrag-server*" } -ErrorAction SilentlyContinue
if ($lightragProcesses) {
    $lightragProcesses | ForEach-Object {
        Write-Host "  - Stopping lightrag process (PID: $($_.Id))" -ForegroundColor Gray
        Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  All Services Stopped" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "You can now restart services with: .\start_all_services.ps1" -ForegroundColor Cyan
Write-Host ""

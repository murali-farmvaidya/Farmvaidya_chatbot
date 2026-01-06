# Start all services (Backend + LightRAG)
# This script starts both the FastAPI backend and LightRAG server

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Starting Farm Vaidya Services" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Stop"

# Get the script directory
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$BACKEND_DIR = $SCRIPT_DIR
$LIGHTRAG_DIR = Join-Path $SCRIPT_DIR "lightrag\Lightrag_main"

# Check if virtual environments exist
$BACKEND_VENV = Join-Path $BACKEND_DIR "venv\Scripts\Activate.ps1"
$LIGHTRAG_VENV = Join-Path $LIGHTRAG_DIR ".venv\Scripts\Activate.ps1"

if (-not (Test-Path $BACKEND_VENV)) {
    Write-Host "ERROR: Backend virtual environment not found at: $BACKEND_VENV" -ForegroundColor Red
    Write-Host "Please create it with: python -m venv venv" -ForegroundColor Yellow
    exit 1
}

if (-not (Test-Path $LIGHTRAG_VENV)) {
    Write-Host "ERROR: LightRAG virtual environment not found at: $LIGHTRAG_VENV" -ForegroundColor Red
    Write-Host "Please run 'uv sync --extra api' in the LightRAG directory" -ForegroundColor Yellow
    exit 1
}

# Copy shared .env file to LightRAG directory
$BACKEND_ENV = Join-Path $BACKEND_DIR ".env"
$LIGHTRAG_ENV = Join-Path $LIGHTRAG_DIR ".env"

if (Test-Path $BACKEND_ENV) {
    Write-Host "Copying shared .env file to LightRAG directory..." -ForegroundColor Cyan
    Copy-Item -Path $BACKEND_ENV -Destination $LIGHTRAG_ENV -Force
    Write-Host "  ✓ .env file synchronized" -ForegroundColor Green
} else {
    Write-Host "WARNING: No .env file found at: $BACKEND_ENV" -ForegroundColor Yellow
    Write-Host "Please create a .env file in the backend/ directory with required variables" -ForegroundColor Yellow
    Write-Host "See .env.example for reference" -ForegroundColor Yellow
}

# Function to check if port is in use
function Test-Port {
    param([int]$Port)
    $connection = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    return $connection -ne $null
}

# Check if ports are already in use
if (Test-Port -Port 8000) {
    Write-Host "WARNING: Port 8000 is already in use. Backend may already be running." -ForegroundColor Yellow
}

if (Test-Port -Port 9621) {
    Write-Host "WARNING: Port 9621 is already in use. LightRAG may already be running." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Starting services..." -ForegroundColor Green
Write-Host ""

# Start Backend Server in a new PowerShell window
Write-Host "[1/2] Starting Backend Server (port 8000)..." -ForegroundColor Cyan
$backendScript = @"
Set-Location '$BACKEND_DIR'
& '$BACKEND_VENV'
Write-Host 'Backend Virtual Environment Activated' -ForegroundColor Green
Write-Host 'Starting Backend Server...' -ForegroundColor Cyan
uvicorn app.main:app --reload --port 8000
"@

Start-Process powershell -ArgumentList @("-NoExit", "-Command", $backendScript) -WindowStyle Normal

Start-Sleep -Seconds 2

# Start LightRAG Server in a new PowerShell window
Write-Host "[2/2] Starting LightRAG Server (port 9621)..." -ForegroundColor Cyan
$lightragScript = @"
Set-Location '$LIGHTRAG_DIR'
& '$LIGHTRAG_VENV'
Write-Host 'LightRAG Virtual Environment Activated' -ForegroundColor Green
Write-Host 'Starting LightRAG Server...' -ForegroundColor Cyan
lightrag-server
"@

Start-Process powershell -ArgumentList @("-NoExit", "-Command", $lightragScript) -WindowStyle Normal

Start-Sleep -Seconds 3

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Services Started Successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Backend API:     http://localhost:8000" -ForegroundColor Cyan
Write-Host "Backend Docs:    http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "LightRAG API:    http://localhost:9621" -ForegroundColor Cyan
Write-Host "LightRAG WebUI:  http://localhost:9621/webui" -ForegroundColor Cyan
Write-Host "LightRAG Docs:   http://localhost:9621/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "To stop all services, run: .\stop_all_services.ps1" -ForegroundColor Yellow
Write-Host "Or close both PowerShell windows that were opened." -ForegroundColor Yellow
Write-Host ""
Write-Host "Press any key to exit this window (services will continue running)..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')

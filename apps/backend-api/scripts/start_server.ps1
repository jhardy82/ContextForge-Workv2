#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Start the TaskMan-v2 Backend API server

.DESCRIPTION
    Starts the FastAPI backend server on port 8002 with hot reload.

.EXAMPLE
    .\scripts\start_server.ps1
    .\scripts\start_server.ps1 -Port 8003
#>
param(
    [int]$Port = 3001,
    [switch]$NoReload
)

$ErrorActionPreference = 'Stop'

# Navigate to backend-api directory
$scriptRoot = Split-Path -Parent $PSScriptRoot
Set-Location $scriptRoot


try {
    Write-Host "Starting TaskMan-v2 Backend API on port $Port..." -ForegroundColor Cyan

    if ($NoReload) {
        & .\.venv\Scripts\python.exe -m uvicorn taskman_api.main:app --app-dir src --host 127.0.0.1 --port $Port
    } else {
        & .\.venv\Scripts\python.exe -m uvicorn taskman_api.main:app --app-dir src --host 127.0.0.1 --port $Port --reload
    }
} catch {
    Write-Error "Failed to start TaskMan-v2 Backend API: $_"
    exit 1
}

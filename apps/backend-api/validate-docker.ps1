# TaskMan-v2 Backend Dockerfile Validation Script
# Tests Docker build, health checks, and PostgreSQL connectivity

# HostPolicy: ModernPS7
# Description: Validates backend Docker infrastructure
# Requires: Docker Desktop, PowerShell 7+

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [ValidateSet('Build', 'Test', 'Health', 'Database', 'All')]
    [string]$Action = 'All',
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipBuild,
    
    [Parameter(Mandatory=$false)]
    [switch]$Cleanup
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Constants
$BACKEND_PATH = Join-Path $PSScriptRoot ".."
$IMAGE_NAME = "taskman-v2-backend:test"
$CONTAINER_NAME = "taskman-backend-test"
$HEALTH_ENDPOINT = "http://localhost:3001/health"

# =============================================================================
# Helper Functions
# =============================================================================
function Write-Step {
    param([string]$Message)
    Write-Host "`n[$(Get-Date -Format 'HH:mm:ss')] $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Failure {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

# =============================================================================
# Test Functions
# =============================================================================
function Test-DockerBuild {
    Write-Step "Building Docker image..."
    
    Push-Location $BACKEND_PATH
    try {
        docker build -t $IMAGE_NAME . 2>&1 | Out-Null
        
        if ($LASTEXITCODE -ne 0) {
            Write-Failure "Docker build failed"
            return $false
        }
        
        Write-Success "Docker image built: $IMAGE_NAME"
        return $true
    }
    finally {
        Pop-Location
    }
}

function Test-ImageSize {
    Write-Step "Checking image size..."
    
    $size = docker images $IMAGE_NAME --format "{{.Size}}"
    Write-Host "Image size: $size"
    
    # Check if multi-stage build was effective (should be < 500MB)
    if ($size -match '(\d+\.?\d*)([MG]B)') {
        $number = [double]$matches[1]
        $unit = $matches[2]
        
        $sizeOk = if ($unit -eq 'MB') { $number -lt 500 } else { $number -lt 0.5 }
        
        if ($sizeOk) {
            Write-Success "Image size is optimal"
        } else {
            Write-Host "⚠️  Image size is larger than expected (target: <500MB)" -ForegroundColor Yellow
        }
    }
}

function Test-ContainerStartup {
    Write-Step "Starting container..."
    
    # Remove existing test container if present
    docker rm -f $CONTAINER_NAME 2>&1 | Out-Null
    
    # Start container with host.docker.internal for external PostgreSQL
    docker run -d `
        --name $CONTAINER_NAME `
        --add-host host.docker.internal:host-gateway `
        -e DATABASE_URL="postgresql://contextforge:contextforge@host.docker.internal:5434/taskman_v2" `
        -p 3001:3001 `
        $IMAGE_NAME
    
    if ($LASTEXITCODE -ne 0) {
        Write-Failure "Container failed to start"
        return $false
    }
    
    Write-Success "Container started: $CONTAINER_NAME"
    
    # Wait for container to be healthy
    Write-Host "Waiting for container to be healthy..."
    $maxAttempts = 30
    $attempt = 0
    
    while ($attempt -lt $maxAttempts) {
        $attempt++
        Start-Sleep -Seconds 2
        
        $health = docker inspect $CONTAINER_NAME --format='{{.State.Health.Status}}' 2>$null
        
        if ($health -eq 'healthy') {
            Write-Success "Container is healthy (after $($attempt * 2)s)"
            return $true
        }
        
        Write-Host "." -NoNewline
    }
    
    Write-Failure "Container did not become healthy within 60 seconds"
    
    # Show logs for debugging
    Write-Host "`nContainer logs:"
    docker logs $CONTAINER_NAME
    
    return $false
}

function Test-HealthEndpoint {
    Write-Step "Testing health endpoint..."
    
    try {
        $response = Invoke-RestMethod -Uri $HEALTH_ENDPOINT -Method Get -TimeoutSec 10
        
        if ($response.status -eq 'healthy') {
            Write-Success "Health endpoint returned: $($response.status)"
            Write-Host "  Environment: $($response.environment)"
            Write-Host "  Version: $($response.version)"
            Write-Host "  Database connected: $($response.database.connected)"
            return $true
        }
        else {
            Write-Failure "Health endpoint returned unexpected status: $($response.status)"
            return $false
        }
    }
    catch {
        Write-Failure "Health endpoint failed: $_"
        return $false
    }
}

function Test-DatabaseConnectivity {
    Write-Step "Testing database connectivity from container..."
    
    # Test PostgreSQL connection from inside container
    $testQuery = "SELECT version();"
    
    $result = docker exec $CONTAINER_NAME `
        psql -h host.docker.internal -p 5434 -U contextforge -d taskman_v2 -c $testQuery 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Database connectivity verified"
        Write-Host "PostgreSQL version: $($result -match 'PostgreSQL' | Select-Object -First 1)"
        return $true
    }
    else {
        Write-Failure "Database connectivity test failed"
        Write-Host "Error: $result"
        return $false
    }
}

function Remove-TestResources {
    Write-Step "Cleaning up test resources..."
    
    docker rm -f $CONTAINER_NAME 2>&1 | Out-Null
    docker rmi -f $IMAGE_NAME 2>&1 | Out-Null
    
    Write-Success "Test resources cleaned up"
}

# =============================================================================
# Main Execution
# =============================================================================
$results = @{
    Build = $null
    ImageSize = $null
    Startup = $null
    Health = $null
    Database = $null
}

try {
    Write-Host "==============================================================================" -ForegroundColor Cyan
    Write-Host "TaskMan-v2 Backend Docker Validation" -ForegroundColor Cyan
    Write-Host "==============================================================================" -ForegroundColor Cyan
    
    if (-not $SkipBuild -and ($Action -in 'Build', 'All')) {
        $results.Build = Test-DockerBuild
        if (-not $results.Build) { throw "Docker build failed" }
        
        $results.ImageSize = Test-ImageSize
    }
    
    if ($Action -in 'Test', 'All') {
        $results.Startup = Test-ContainerStartup
        if (-not $results.Startup) { throw "Container startup failed" }
    }
    
    if ($Action -in 'Health', 'All') {
        $results.Health = Test-HealthEndpoint
    }
    
    if ($Action -in 'Database', 'All') {
        $results.Database = Test-DatabaseConnectivity
    }
    
    # Summary
    Write-Host "`n==============================================================================" -ForegroundColor Cyan
    Write-Host "Test Results Summary" -ForegroundColor Cyan
    Write-Host "==============================================================================" -ForegroundColor Cyan
    
    $allPassed = $true
    foreach ($test in $results.GetEnumerator() | Where-Object { $null -ne $_.Value }) {
        $status = if ($test.Value) { "✅ PASS" } else { "❌ FAIL"; $allPassed = $false }
        Write-Host "$($test.Key.PadRight(15)): $status"
    }
    
    if ($allPassed) {
        Write-Host "`n🎉 All tests passed! Backend Docker infrastructure is ready." -ForegroundColor Green
    }
    else {
        Write-Host "`n⚠️  Some tests failed. Review logs above for details." -ForegroundColor Yellow
    }
}
catch {
    Write-Failure "Validation failed: $_"
    exit 1
}
finally {
    if ($Cleanup) {
        Remove-TestResources
    }
}

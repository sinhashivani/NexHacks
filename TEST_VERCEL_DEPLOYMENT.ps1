# Vercel Deployment Testing Script
# Tests all endpoints and functionality

param(
    [string]$ApiUrl = "https://nexhacks-nu.vercel.app"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Vercel Deployment Test Suite" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "API URL: $ApiUrl" -ForegroundColor Yellow
Write-Host ""

$testsPassed = 0
$testsFailed = 0
$warnings = 0

function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Url,
        [string]$Method = "GET",
        [object]$Body = $null,
        [int]$ExpectedStatus = 200
    )
    
    Write-Host "[TEST] $Name..." -NoNewline
    
    try {
        $params = @{
            Uri = $Url
            Method = $Method
            Headers = @{
                "Content-Type" = "application/json"
            }
            ErrorAction = "Stop"
        }
        
        if ($Body) {
            $params.Body = ($Body | ConvertTo-Json -Depth 10)
        }
        
        $response = Invoke-RestMethod @params
        $statusCode = 200
        
        Write-Host " PASS" -ForegroundColor Green
        Write-Host "      Status: $statusCode" -ForegroundColor Gray
        if ($response -is [PSCustomObject] -or $response -is [Hashtable]) {
            $summary = $response | ConvertTo-Json -Depth 1 -Compress
            if ($summary.Length -gt 100) {
                $summary = $summary.Substring(0, 100) + "..."
            }
            Write-Host "      Response: $summary" -ForegroundColor Gray
        }
        $script:testsPassed++
        return $true
    }
    catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        if ($statusCode -eq $ExpectedStatus) {
            Write-Host " PASS (Expected $ExpectedStatus)" -ForegroundColor Green
            $script:testsPassed++
            return $true
        } else {
            Write-Host " FAIL" -ForegroundColor Red
            Write-Host "      Error: $($_.Exception.Message)" -ForegroundColor Red
            if ($statusCode) {
                Write-Host "      Status: $statusCode (Expected: $ExpectedStatus)" -ForegroundColor Red
            }
            $script:testsFailed++
            return $false
        }
    }
}

# Phase 1: Basic Connectivity (No Database Required)
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Phase 1: Basic Connectivity Tests" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Test-Endpoint -Name "Root Endpoint" -Url "$ApiUrl/"

Test-Endpoint -Name "CORS Test Endpoint" -Url "$ApiUrl/test-cors"

# Test Favicon (should return 204)
Write-Host "[TEST] Favicon Handler..." -NoNewline
try {
    $response = Invoke-WebRequest -Uri "$ApiUrl/favicon.ico" -Method HEAD -ErrorAction Stop
    if ($response.StatusCode -eq 204) {
        Write-Host " PASS (204 No Content)" -ForegroundColor Green
        $testsPassed++
    } else {
        Write-Host " WARNING (Expected 204, got $($response.StatusCode))" -ForegroundColor Yellow
        $warnings++
    }
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    if ($statusCode -eq 204) {
        Write-Host " PASS (204 No Content)" -ForegroundColor Green
        $testsPassed++
    } else {
        Write-Host " FAIL" -ForegroundColor Red
        Write-Host "      Status: $statusCode" -ForegroundColor Red
        $testsFailed++
    }
}

# Phase 2: Database Connectivity Tests
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Phase 2: Database Connectivity Tests" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Test-Endpoint -Name "Trending Markets" -Url "$ApiUrl/markets/trending?limit=5"

# Test Similar Markets
$testTitle = [System.Uri]::EscapeDataString("Who will Trump nominate as Fed Chair?")
Test-Endpoint -Name "Similar Markets" -Url "$ApiUrl/similar?event_title=$testTitle&limit=3"

Test-Endpoint -Name "Related Markets" -Url "$ApiUrl/related?limit=3"

# Phase 3: Advanced API Tests (Optional)
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Phase 3: Advanced API Tests (Optional)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Test-Endpoint -Name "Gamma Tags" -Url "$ApiUrl/gamma/tags" -ExpectedStatus 200

# Phase 4: Response Time Check
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Phase 4: Performance Tests" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[TEST] Response Time..." -NoNewline
try {
    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    $response = Invoke-RestMethod -Uri "$ApiUrl/" -ErrorAction Stop
    $stopwatch.Stop()
    $ms = $stopwatch.ElapsedMilliseconds
    
    if ($ms -lt 1000) {
        Write-Host " PASS" -ForegroundColor Green
        Write-Host "      Response time: ${ms}ms" -ForegroundColor Gray
        $testsPassed++
    } else {
        Write-Host " WARNING" -ForegroundColor Yellow
        Write-Host "      Response time: ${ms}ms (slow)" -ForegroundColor Yellow
        $warnings++
    }
} catch {
    Write-Host " FAIL" -ForegroundColor Red
    Write-Host "      Error: $($_.Exception.Message)" -ForegroundColor Red
    $testsFailed++
}

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Test Results Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Passed: $testsPassed" -ForegroundColor Green
Write-Host "Failed: $testsFailed" -ForegroundColor $(if ($testsFailed -eq 0) { "Green" } else { "Red" })
Write-Host "Warnings: $warnings" -ForegroundColor $(if ($warnings -eq 0) { "Green" } else { "Yellow" })
Write-Host ""

if ($testsFailed -eq 0) {
    Write-Host "✅ All critical tests passed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Cyan
    Write-Host "1. Test in browser console (CORS test)" -ForegroundColor White
    Write-Host "2. Update extension to use: $ApiUrl" -ForegroundColor White
    Write-Host "3. Reload extension and test on Polymarket" -ForegroundColor White
} else {
    Write-Host "❌ Some tests failed. Check:" -ForegroundColor Red
    Write-Host "   1. Environment variables in Vercel dashboard" -ForegroundColor Yellow
    Write-Host "   2. Database connectivity (SUPABASE_URL, SUPABASE_ANON_KEY)" -ForegroundColor Yellow
    Write-Host "   3. Vercel deployment logs" -ForegroundColor Yellow
}

Write-Host ""

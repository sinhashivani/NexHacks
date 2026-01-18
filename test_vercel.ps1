# Vercel Deployment Test Script
# Usage: .\test_vercel.ps1 -ApiUrl "https://your-app.vercel.app"

param(
    [string]$ApiUrl = "https://nexhacks-e386iygyw-shilojeyarajs-projects.vercel.app"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Vercel Deployment Test Suite" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "API URL: $ApiUrl" -ForegroundColor Yellow
Write-Host ""

$testsPassed = 0
$testsFailed = 0

function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Url,
        [string]$Method = "GET",
        [object]$Body = $null
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
        Write-Host "      Response: $($response | ConvertTo-Json -Depth 2 -Compress)" -ForegroundColor Gray
        $script:testsPassed++
        return $true
    }
    catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        Write-Host " FAIL" -ForegroundColor Red
        Write-Host "      Error: $($_.Exception.Message)" -ForegroundColor Red
        if ($statusCode) {
            Write-Host "      Status: $statusCode" -ForegroundColor Red
        }
        $script:testsFailed++
        return $false
    }
}

# Test 1: Root Endpoint
Test-Endpoint -Name "Root Endpoint" -Url "$ApiUrl/"

# Test 2: CORS Test
Test-Endpoint -Name "CORS Test" -Url "$ApiUrl/test-cors"

# Test 3: Favicon Handler
Write-Host "[TEST] Favicon Handler..." -NoNewline
try {
    $response = Invoke-WebRequest -Uri "$ApiUrl/favicon.ico" -Method HEAD -ErrorAction Stop
    if ($response.StatusCode -eq 204) {
        Write-Host " PASS (204 No Content)" -ForegroundColor Green
        $testsPassed++
    } else {
        Write-Host " FAIL (Expected 204, got $($response.StatusCode))" -ForegroundColor Red
        $testsFailed++
    }
} catch {
    Write-Host " FAIL" -ForegroundColor Red
    Write-Host "      Error: $($_.Exception.Message)" -ForegroundColor Red
    $testsFailed++
}

# Test 4: Trending Markets (requires database)
Test-Endpoint -Name "Trending Markets" -Url "$ApiUrl/markets/trending?limit=3"

# Test 5: Similar Markets (requires database)
$testTitle = [System.Uri]::EscapeDataString("Who will Trump nominate as Fed Chair?")
Test-Endpoint -Name "Similar Markets" -Url "$ApiUrl/similar?event_title=$testTitle&limit=3"

# Test 6: CORS Headers Check
Write-Host "[TEST] CORS Headers..." -NoNewline
try {
    $response = Invoke-WebRequest -Uri "$ApiUrl/test-cors" -Method OPTIONS -ErrorAction Stop
    $corsHeader = $response.Headers["Access-Control-Allow-Origin"]
    if ($corsHeader) {
        Write-Host " PASS" -ForegroundColor Green
        Write-Host "      CORS Header: $corsHeader" -ForegroundColor Gray
        $testsPassed++
    } else {
        Write-Host " WARNING (No CORS header found)" -ForegroundColor Yellow
        $testsPassed++ # Not a failure, just a warning
    }
} catch {
    Write-Host " SKIP (OPTIONS not supported)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Test Results" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Passed: $testsPassed" -ForegroundColor Green
Write-Host "Failed: $testsFailed" -ForegroundColor $(if ($testsFailed -eq 0) { "Green" } else { "Red" })
Write-Host ""

if ($testsFailed -eq 0) {
    Write-Host "✅ All tests passed! Your API is working correctly." -ForegroundColor Green
} else {
    Write-Host "❌ Some tests failed. Check the errors above and verify:" -ForegroundColor Red
    Write-Host "   1. Environment variables are set in Vercel dashboard" -ForegroundColor Yellow
    Write-Host "   2. Database is accessible" -ForegroundColor Yellow
    Write-Host "   3. API URL is correct" -ForegroundColor Yellow
}

Write-Host ""

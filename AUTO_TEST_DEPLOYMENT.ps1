# Automated Deployment Testing Script
# Tests all endpoints and reports results

param(
    [string]$ApiUrl = "https://nexhacks-nu.vercel.app"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Automated Deployment Test Suite" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "API URL: $ApiUrl" -ForegroundColor Yellow
Write-Host "Waiting 5 seconds for deployment to propagate..." -ForegroundColor Gray
Start-Sleep -Seconds 5
Write-Host ""

$results = @()
$totalTests = 0
$passedTests = 0
$failedTests = 0

function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Url,
        [string]$Method = "GET",
        [object]$Body = $null,
        [int]$ExpectedStatus = 200,
        [int]$TimeoutSeconds = 10
    )
    
    $script:totalTests++
    Write-Host "[TEST $script:totalTests] $Name..." -NoNewline
    
    try {
        $params = @{
            Uri = $Url
            Method = $Method
            Headers = @{
                "Content-Type" = "application/json"
            }
            ErrorAction = "Stop"
            TimeoutSec = $TimeoutSeconds
        }
        
        if ($Body) {
            $params.Body = ($Body | ConvertTo-Json -Depth 10)
        }
        
        $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
        $response = Invoke-RestMethod @params
        $stopwatch.Stop()
        $responseTime = $stopwatch.ElapsedMilliseconds
        
        Write-Host " PASS" -ForegroundColor Green
        Write-Host "      Status: 200 OK | Response Time: ${responseTime}ms" -ForegroundColor Gray
        
        $script:results += [PSCustomObject]@{
            Test = $Name
            Status = "PASS"
            ResponseTime = $responseTime
            Details = "200 OK"
        }
        $script:passedTests++
        return $true
    }
    catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        if ($statusCode -eq $ExpectedStatus) {
            Write-Host " PASS (Expected $ExpectedStatus)" -ForegroundColor Green
            $script:results += [PSCustomObject]@{
                Test = $Name
                Status = "PASS"
                ResponseTime = 0
                Details = "Expected $ExpectedStatus"
            }
            $script:passedTests++
            return $true
        } else {
            Write-Host " FAIL" -ForegroundColor Red
            Write-Host "      Error: $($_.Exception.Message)" -ForegroundColor Red
            if ($statusCode) {
                Write-Host "      Status: $statusCode (Expected: $ExpectedStatus)" -ForegroundColor Red
            }
            
            $script:results += [PSCustomObject]@{
                Test = $Name
                Status = "FAIL"
                ResponseTime = 0
                Details = "Status: $statusCode - $($_.Exception.Message)"
            }
            $script:failedTests++
            return $false
        }
    }
}

# Phase 1: Basic Connectivity
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Phase 1: Basic Connectivity" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Test-Endpoint -Name "Root Endpoint" -Url "$ApiUrl/"

Test-Endpoint -Name "CORS Test" -Url "$ApiUrl/test-cors"

# Favicon test
$script:totalTests++
Write-Host "[TEST $script:totalTests] Favicon Handler..." -NoNewline
try {
    $response = Invoke-WebRequest -Uri "$ApiUrl/favicon.ico" -Method HEAD -ErrorAction Stop -TimeoutSec 10
    if ($response.StatusCode -eq 204) {
        Write-Host " PASS (204 No Content)" -ForegroundColor Green
        $script:results += [PSCustomObject]@{Test="Favicon Handler"; Status="PASS"; ResponseTime=0; Details="204 No Content"}
        $script:passedTests++
    } else {
        Write-Host " WARNING (Got $($response.StatusCode), expected 204)" -ForegroundColor Yellow
        $script:results += [PSCustomObject]@{Test="Favicon Handler"; Status="WARN"; ResponseTime=0; Details="Status: $($response.StatusCode)"}
        $script:passedTests++
    }
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    if ($statusCode -eq 204) {
        Write-Host " PASS (204 No Content)" -ForegroundColor Green
        $script:results += [PSCustomObject]@{Test="Favicon Handler"; Status="PASS"; ResponseTime=0; Details="204 No Content"}
        $script:passedTests++
    } else {
        Write-Host " FAIL" -ForegroundColor Red
        Write-Host "      Status: $statusCode" -ForegroundColor Red
        $script:results += [PSCustomObject]@{Test="Favicon Handler"; Status="FAIL"; ResponseTime=0; Details="Status: $statusCode"}
        $script:failedTests++
    }
}

# Phase 2: Database Connectivity
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Phase 2: Database Connectivity" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Test-Endpoint -Name "Trending Markets" -Url "$ApiUrl/markets/trending?limit=5" -TimeoutSeconds 15

$testTitle = [System.Uri]::EscapeDataString("Who will Trump nominate as Fed Chair?")
Test-Endpoint -Name "Similar Markets" -Url "$ApiUrl/similar?event_title=$testTitle&limit=3" -TimeoutSeconds 15

Test-Endpoint -Name "Related Markets" -Url "$ApiUrl/related?limit=3" -TimeoutSeconds 15

# Phase 3: Performance Tests
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Phase 3: Performance Tests" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$performanceTests = @()
1..5 | ForEach-Object {
    Write-Host "[PERF TEST $_/5] Root endpoint..." -NoNewline
    try {
        $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
        $response = Invoke-RestMethod -Uri "$ApiUrl/" -ErrorAction Stop -TimeoutSec 10
        $stopwatch.Stop()
        $ms = $stopwatch.ElapsedMilliseconds
        $performanceTests += $ms
        Write-Host " ${ms}ms" -ForegroundColor Gray
    } catch {
        Write-Host " FAILED" -ForegroundColor Red
    }
}

if ($performanceTests.Count -gt 0) {
    $avg = ($performanceTests | Measure-Object -Average).Average
    $min = ($performanceTests | Measure-Object -Minimum).Minimum
    $max = ($performanceTests | Measure-Object -Maximum).Maximum
    Write-Host ""
    Write-Host "Performance Summary:" -ForegroundColor Cyan
    Write-Host "  Average: $([math]::Round($avg, 2))ms" -ForegroundColor Gray
    Write-Host "  Min: ${min}ms" -ForegroundColor Gray
    Write-Host "  Max: ${max}ms" -ForegroundColor Gray
}

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Test Results Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$results | Format-Table -AutoSize

Write-Host ""
Write-Host "Total Tests: $totalTests" -ForegroundColor Cyan
Write-Host "Passed: $passedTests" -ForegroundColor Green
Write-Host "Failed: $failedTests" -ForegroundColor $(if ($failedTests -eq 0) { "Green" } else { "Red" })
Write-Host ""

$successRate = if ($totalTests -gt 0) { [math]::Round(($passedTests / $totalTests) * 100, 1) } else { 0 }
Write-Host "Success Rate: $successRate%" -ForegroundColor $(if ($successRate -ge 80) { "Green" } elseif ($successRate -ge 50) { "Yellow" } else { "Red" })
Write-Host ""

if ($failedTests -eq 0) {
    Write-Host "✅ ALL TESTS PASSED! Deployment is successful!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Your API is ready at: $ApiUrl" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Yellow
    Write-Host "1. Update extension to use: $ApiUrl" -ForegroundColor White
    Write-Host "2. Reload extension in Chrome" -ForegroundColor White
    Write-Host "3. Test on Polymarket" -ForegroundColor White
} else {
    Write-Host "❌ Some tests failed. Check:" -ForegroundColor Red
    Write-Host "   1. Vercel logs: vercel logs $ApiUrl" -ForegroundColor Yellow
    Write-Host "   2. Environment variables in Vercel dashboard" -ForegroundColor Yellow
    Write-Host "   3. Database connectivity" -ForegroundColor Yellow
}

Write-Host ""

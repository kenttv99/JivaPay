# Скрипт для проверки сборки всех приложений JivaPay Frontend
Write-Host "🔍 Проверка сборки всех приложений JivaPay..." -ForegroundColor Green

$apps = @("admin_app", "trader_app", "support_app", "merchant_app", "teamlead_app")
$results = @()

foreach ($app in $apps) {
    Write-Host "📦 Сборка $app..." -ForegroundColor Yellow
    
    Set-Location $app
    $buildResult = npm run build 2>&1
    $exitCode = $LASTEXITCODE
    
    if ($exitCode -eq 0) {
        Write-Host "✅ $app - успешно собрано" -ForegroundColor Green
        $results += @{App=$app; Status="SUCCESS"; Error=$null}
    } else {
        Write-Host "❌ $app - ошибка сборки" -ForegroundColor Red
        $results += @{App=$app; Status="FAILED"; Error=$buildResult}
    }
    
    Set-Location ..
}

Write-Host "`n📊 Итоговые результаты:" -ForegroundColor Cyan
foreach ($result in $results) {
    $status = if ($result.Status -eq "SUCCESS") { "✅" } else { "❌" }
    Write-Host "$status $($result.App) - $($result.Status)" -ForegroundColor $(if ($result.Status -eq "SUCCESS") { "Green" } else { "Red" })
}

$successCount = ($results | Where-Object { $_.Status -eq "SUCCESS" }).Count
$totalCount = $results.Count

Write-Host "`n🎯 Общий результат: $successCount из $totalCount приложений успешно собраны" -ForegroundColor $(if ($successCount -eq $totalCount) { "Green" } else { "Yellow" })

if ($successCount -eq $totalCount) {
    Write-Host "🚀 Все приложения готовы к развертыванию!" -ForegroundColor Green
} else {
    Write-Host "⚠️  Есть проблемы с некоторыми приложениями" -ForegroundColor Yellow
    
    $failed = $results | Where-Object { $_.Status -eq "FAILED" }
    foreach ($failure in $failed) {
        Write-Host "`n❌ Ошибки в $($failure.App):" -ForegroundColor Red
        Write-Host $failure.Error -ForegroundColor Red
    }
} 
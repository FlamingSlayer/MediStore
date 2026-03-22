param(
    [string]$PythonExe = "C:/Users/Anil Jha/AppData/Local/Programs/Python/Python39/python.exe",
    [string]$Host = "127.0.0.1",
    [int]$Port = 8000,
    [switch]$SkipSeed
)

$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

Write-Host "Stopping stale Django runserver processes..." -ForegroundColor Yellow
Get-CimInstance Win32_Process |
    Where-Object { $_.Name -match 'python(\.exe)?' -and $_.CommandLine -match 'manage\.py runserver' } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }

Write-Host "Running migrations..." -ForegroundColor Cyan
& $PythonExe manage.py migrate

if (-not $SkipSeed) {
    Write-Host "Seeding sample data (if empty)..." -ForegroundColor Cyan
    & $PythonExe manage.py seed_sample_data --if-empty
}

Write-Host "Starting Django server at http://$Host`:$Port/" -ForegroundColor Green
& $PythonExe manage.py runserver "$Host`:$Port"

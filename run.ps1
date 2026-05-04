# VaxCheck launcher for Windows PowerShell
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

# Kill processes on our ports
$ports = @(8000, 3000)
foreach ($port in $ports) {
    $pid = (Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue | Select-Object -First 1).OwningProcess
    if ($pid) {
        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
    }
}
Start-Sleep -Seconds 1

# Cleanup on Ctrl+C
$apiJob = $null
Register-EngineEvent -SourceIdentifier PowerShell.Exiting -Action {
    if ($apiJob) { Stop-Job $apiJob }
}

Write-Host "================================================="
Write-Host "  API  -> http://localhost:8000"
Write-Host "  FE   -> http://localhost:3000"
Write-Host "  Ctrl+C to stop both"
Write-Host "================================="

# Activate venv and start API
. .\.venv\Scripts\Activate.ps1
$apiJob = Start-Job -ScriptBlock {
    Set-Location $using:PSScriptRoot
    . .\.venv\Scripts\Activate.ps1
    uvicorn vaxcheck.api.main:app --host 0.0.0.0 --port 8000 --reload
}

Start-Sleep -Seconds 1

# Start frontend
Set-Location frontend
npm run dev

# Cleanup
if ($apiJob) { Stop-Job $apiJob }

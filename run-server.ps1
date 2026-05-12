param(
    [string]$HostName = "127.0.0.1",
    [int]$Port = 8000,
    [string]$DatabaseUrl = $env:DATABASE_URL,
    [string]$Python = "C:\Program Files\PostgreSQL\18\pgAdmin 4\python\python.exe"
)

if ($DatabaseUrl -and $DatabaseUrl.Contains("YOUR_PASSWORD")) {
    Write-Host "DATABASE_URL доторх YOUR_PASSWORD гэдгийг PostgreSQL-ийн жинхэнэ password-оор солино уу." -ForegroundColor Red
    Write-Host 'Жишээ: $env:DATABASE_URL="postgresql+psycopg://postgres:postgres_password@localhost:5432/feedback_admin"'
    exit 1
}

if ($DatabaseUrl) {
    $env:DATABASE_URL = $DatabaseUrl
}

$packagesPath = Join-Path $PSScriptRoot ".python\uvicorn"
if (-not (Test-Path $packagesPath)) {
    & $Python -m pip install -r "$PSScriptRoot\requirements.txt" --target "$PSScriptRoot\.python"
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}

& $Python "$PSScriptRoot\run_server.py" --host $HostName --port $Port

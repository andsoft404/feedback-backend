param(
    [string]$HostName = "localhost",
    [string]$Port = "5432",
    [string]$User = "postgres",
    [string]$Database = "feedback_admin",
    [string]$Password = $env:PGPASSWORD
)

if (-not $Password) {
    throw "PostgreSQL password is required. Pass -Password or set `$env:PGPASSWORD."
}

$env:PGPASSWORD = $Password
$psql = "C:\Program Files\PostgreSQL\18\bin\psql.exe"
if (-not (Test-Path $psql)) {
    $psql = "psql.exe"
}

$ensureDbSql = @"
SELECT 'CREATE DATABASE ' || quote_ident(:'database_name')
WHERE NOT EXISTS (
    SELECT FROM pg_database WHERE datname = :'database_name'
)\gexec
"@

$tempSql = New-TemporaryFile
try {
    Set-Content -Path $tempSql -Value $ensureDbSql -Encoding UTF8
    & $psql -w -h $HostName -p $Port -U $User -d postgres -v database_name="$Database" -f $tempSql
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }

    & $psql -w -h $HostName -p $Port -U $User -d $Database -f "$PSScriptRoot\sql\seed_admin.sql"
    exit $LASTEXITCODE
}
finally {
    Remove-Item -LiteralPath $tempSql -Force -ErrorAction SilentlyContinue
}

$env:WEB_PORT = "80"
$env:SECRET = "very_secret"
$env:POSTGRES_CONNECTION_STRING = "postgresql://usr:pass@localhost:5432/database"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$pythonScriptPath = Join-Path -Path $scriptDir -ChildPath "\main.py"
python $pythonScriptPath

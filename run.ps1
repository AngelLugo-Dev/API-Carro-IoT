# Ejecuta el backend en Windows PowerShell
if (-Not (Test-Path .\.venv)) {
  python -m venv .venv
}
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:PYTHONPATH = "$PSScriptRoot" + ([IO.Path]::PathSeparator) + $env:PYTHONPATH
python -m uvicorn app.main:app --host 0.0.0.0 --port 5500 --workers 1
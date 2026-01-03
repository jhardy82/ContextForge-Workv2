$env:PYTHONPATH = 'C:\Users\James\Documents\Github\GHrepos\SCCMScripts\TaskMan-v2\backend-api\src'
Write-Host 'Starting Uvicorn...'
Start-Process -FilePath 'python' -ArgumentList '-m uvicorn taskman_api.main:app --port 3001 --host 127.0.0.1' -RedirectStandardOutput 'backend.log' -RedirectStandardError 'backend_error.log' -NoNewWindow

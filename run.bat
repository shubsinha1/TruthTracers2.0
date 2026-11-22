@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
  py -3 -m venv .venv
  if errorlevel 1 goto failed
)
.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
if errorlevel 1 goto failed
if not exist .env copy .env.example .env >nul
echo Open http://127.0.0.1:8000 in your browser once the server starts.
.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
if errorlevel 1 goto failed
exit /b 0
:failed
echo Startup failed. Check the error above. Python 3.10 or newer with the py launcher is required.
pause
exit /b 1

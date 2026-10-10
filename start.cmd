@echo off
rem Start KawTeam: FastAPI on :8000 and Next.js on :3000, then open the browser.
setlocal
cd /d "%~dp0"

if not exist "apps\api\.env" (
  echo Missing apps\api\.env. See "Supabase setup" in README.md.
  pause
  exit /b 1
)
if not exist "apps\web\.env.local" (
  echo Missing apps\web\.env.local. See "Supabase setup" in README.md.
  pause
  exit /b 1
)

if not exist "apps\api\.venv\Scripts\python.exe" (
  echo Creating the Python environment...
  python -m venv "apps\api\.venv" || (pause & exit /b 1)
  "apps\api\.venv\Scripts\python.exe" -m pip install -q -r "apps\api\requirements.txt" || (pause & exit /b 1)
)
if not exist "apps\web\node_modules" (
  echo Installing web dependencies...
  pushd "apps\web"
  call npm install --no-save --no-audit --no-fund || (popd & pause & exit /b 1)
  popd
)

start "KawTeam API" /D "%~dp0apps\api" cmd /k ".venv\Scripts\python.exe -m uvicorn kawteam.main:app --app-dir src --reload --port 8000"
start "KawTeam Web" /D "%~dp0apps\web" cmd /k "npm run dev"

echo Waiting for KawTeam to start...
powershell -NoProfile -Command "for($i=0;$i -lt 90;$i++){try{Invoke-WebRequest http://localhost:3000 -UseBasicParsing -TimeoutSec 10 | Out-Null; exit 0}catch{Start-Sleep -Seconds 1}}; exit 1"
if errorlevel 1 (
  echo KawTeam did not respond on http://localhost:3000. Check the "KawTeam Web" window.
  pause
  exit /b 1
)
start "" http://localhost:3000
echo KawTeam is running at http://localhost:3000. Close the two server windows to stop it.

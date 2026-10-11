@echo off
set "ROOT_DIR=%~dp0.."

echo Starting Next.js Frontend...
start "Frontend (Next.js)" cmd /k "cd /d "%ROOT_DIR%\frontend" && npm run dev"

echo Starting FastAPI Backend...
start "Backend (FastAPI)" cmd /k "cd /d "%ROOT_DIR%\backend" && call "%ROOT_DIR%\.venv\Scripts\activate.bat" && uvicorn app.main:app --reload --port 8000"

echo Both servers are starting in separate windows!


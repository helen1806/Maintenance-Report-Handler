@echo off
echo Starting Next.js Frontend...
start cmd /k "cd ..\frontend && npm run dev"

echo Starting FastAPI Backend...
start cmd /k "cd ..\backend && .\.venv\Scripts\activate && uvicorn app.main:app --reload"

echo Both servers are starting in separate windows!

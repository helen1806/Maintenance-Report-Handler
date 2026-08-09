#!/bin/bash

# Start the Celery worker in the background WITH ONLY 1 CONCURRENT PROCESS
celery -A app.celery_app worker --loglevel=info --concurrency=1 &

# Start the FastAPI web server in the foreground
uvicorn app.main:app --host 0.0.0.0 --port $PORT

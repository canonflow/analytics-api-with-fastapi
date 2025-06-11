#!/bin/bash

source /opt/venv/bin/activate

cd /code
RUN_PORT=${PORT:-8000}
RUN_HOST=${HOST:-0.0.0.0} # HOST=[::] # IPv6

gunicorn -k uvicorn.workers.UvicornWorker -b $RUN_HOST:$RUN_PORT main:app
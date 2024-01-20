#!/bin/sh
service postgresql start
service redis-server start
service cron start
service ntp start
cd /home/media && uvicorn app.app:app --host 0.0.0.0 --port 80 --reload

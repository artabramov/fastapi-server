#!/bin/sh
service postgresql start
service redis-server start
service cron start
service ntp start
service apache2 start
cd /memo && uvicorn app.app:app --host 0.0.0.0 --port 8080 --reload

#!/bin/sh
service postgresql start
service redis-server start
service cron start
service ntp start
service apache2 start
cd /memo && uvicorn app.app:app --host 127.0.0.1 --port 8080 --reload
/usr/sbin/apache2ctl -DFOREGROUND

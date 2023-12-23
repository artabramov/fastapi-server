docker build --no-cache -t memo-server .
docker run -dit -p 80:8080 -p 5432:5432 --name memo-server memo-server
docker exec memo-server sudo -u postgres psql -c "CREATE USER memo WITH PASSWORD 'he7w2rLY4Y8pFk2u';"
docker exec memo-server sudo -u postgres psql -c "CREATE DATABASE memo;"

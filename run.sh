docker rm media-server
docker rmi media-server
docker build --no-cache -t media-server .
docker run -dit -p 80:80 -p 8081:8081 -p 5432:5432 --name media-server media-server
docker exec media-server sudo -u postgres psql -c "CREATE USER media WITH PASSWORD 'he7w2rLY4Y8pFk2u';"
docker exec media-server sudo -u postgres psql -c "CREATE DATABASE media;"

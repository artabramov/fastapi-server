docker build --no-cache -t mediaserver .
docker run -dit -p 80:80 -p 8081:8081 -p 5432:5432 --name mediaserver mediaserver
docker exec mediaserver sudo -u postgres psql -c "CREATE USER media WITH PASSWORD 'he7w2rLY4Y8pFk2u';"
docker exec mediaserver sudo -u postgres psql -c "CREATE DATABASE media;"

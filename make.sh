docker build --no-cache -t depot-server .
docker run -dit -p 80:80 -p 8081:8081 -p 5432:5432 --name depot-server depot-server
docker exec depot-server sudo -u postgres psql -c "CREATE USER depot WITH PASSWORD 'he7w2rLY4Y8pFk2u';"
docker exec depot-server sudo -u postgres psql -c "CREATE DATABASE depot;"

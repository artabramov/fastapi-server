# memo

### Build the image from a Dockerfile
```
docker build --no-cache -t memo-server .
```

### Create and run a new container from the image
```
docker run -dit -p 80:8080 -p 5432:5432 -v postgres-data:/var/lib/postgresql/14/main --name memo-server memo-server
```

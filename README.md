# memo

### Build the image from a Dockerfile
```
docker build --no-cache -t memo-server .
```

### Create and run a new container from the image
```
docker run -dit -p 80:8080 --name memo-server memo-server
```

# memo

### How to install the app
```
./make.sh
```

### How to allow remote connections to Postgres
Install VIM
```
apt-get install -y vim
```
Open postgres.conf
```
vim /etc/postgresql/14/main/postgresql.conf
```
And change the line:
```
listen_addresses = '*'
```
Open pg_hba.conf
```
vim /etc/postgresql/14/main/pg_hba.conf
```
And add the line:
```
host all all 0.0.0.0/0 md5
```

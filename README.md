# memo

### How to install
```
./make.sh
```

### How to allow remote connection to Postgres
Install VIM
```
apt-get install -y vim
```
Edit postgres.conf
```
vim /etc/postgresql/14/main/postgresql.conf
```
And change the line:
```
listen_addresses = '*'
```
Edit pg_hba.conf
```
vim /etc/postgresql/14/main/pg_hba.conf
```
And add the line
```
host all all 0.0.0.0/0 md5
```

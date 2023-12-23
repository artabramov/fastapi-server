FROM ubuntu:latest
RUN apt-get update
ENV DEBIAN_FRONTEND=noninteractive

ADD . /memo
WORKDIR /memo

RUN apt install software-properties-common -y
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt install -y python3.13
RUN apt-get install -y python3-dev
RUN apt-get install -y python3-pip
RUN alias python3="/usr/bin/python3.13"

RUN apt install -y postgresql postgresql-contrib
RUN apt-get install -y sudo
RUN service postgresql start
RUN sudo -u postgres psql -c "CREATE USER memo WITH PASSWORD 'he7w2rLY4Y8pFk2u';"
RUN sudo -u postgres psql -c "CREATE DATABASE memo;"

RUN apt-get install -y redis
RUN apt-get install -y cron
RUN apt-get upgrade -y cron
RUN apt-get install -y ntp
RUN apt install -y git

RUN apt-get install -y apache2 apache2-dev
RUN a2enmod rewrite
RUN a2enmod proxy
RUN apt-get clean
RUN cp --force ./000-default.conf /etc/apache2/sites-available/000-default.conf

RUN pip3 install fastapi[all]
RUN pip3 install uvicorn[standard]
RUN pip3 install python-dotenv
RUN pip3 install SQLAlchemy
RUN pip3 install psycopg2-binary
RUN pip3 install redis
RUN pip3 install pyotp
RUN pip3 install qrcode[pil]
RUN pip3 install cryptography
RUN pip3 install PyJWT
RUN pip3 install filetype
RUN pip3 install flake8
RUN pip3 install flake8-docstrings
RUN pip3 install coverage
RUN pip3 install python-crontab
RUN pip3 freeze > /memo/requirements.txt

EXPOSE 80
ENTRYPOINT ["/memo/entrypoint.sh"]

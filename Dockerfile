FROM ubuntu:latest
RUN apt-get update
ENV DEBIAN_FRONTEND=noninteractive

ADD . /depot
WORKDIR /depot

RUN apt install software-properties-common -y
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt install -y python3.13
RUN apt-get install -y python3-dev
RUN apt-get install -y python3-pip
RUN alias python3="/usr/bin/python3.13"

RUN apt install -y postgresql postgresql-contrib
RUN apt-get install -y redis
RUN apt-get install -y cron
RUN apt-get upgrade -y cron
RUN apt-get install -y ntp
RUN apt-get install -y sudo
RUN apt install -y git

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
RUN pip3 install aiofiles
RUN pip3 install flake8
RUN pip3 install flake8-docstrings
RUN pip3 install coverage
RUN pip3 install python-crontab
RUN pip3 freeze > /depot/requirements.txt

EXPOSE 80
ENTRYPOINT ["/depot/entrypoint.sh"]

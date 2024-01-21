FROM ubuntu:latest
RUN apt-get update
ENV DEBIAN_FRONTEND=noninteractive

ADD . /usr/local/media-server
WORKDIR /usr/local/media-server

RUN apt install -y software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt install -y python3.11 python3.11-dev
RUN apt-get install -y python3-pip
RUN unlink /usr/bin/python3
RUN ln -s /usr/bin/python3.11 /usr/bin/python3

RUN pip3 install python-dotenv
RUN pip3 install SQLAlchemy
RUN pip3 install psycopg2-binary
RUN pip3 install fastapi[all]
RUN pip3 install uvicorn[standard]
RUN pip3 install redis
RUN pip3 install pyotp
RUN pip3 install qrcode[pil]
RUN pip3 install cryptography
RUN pip3 install cffi
RUN pip3 install PyJWT
RUN pip3 install filetype
RUN pip3 install aiofiles
RUN pip3 install flake8
RUN pip3 install flake8-docstrings
RUN pip3 install coverage
RUN pip3 install python-crontab
RUN pip3 freeze > /usr/local/media-server/requirements.txt

RUN mkdir /var/log/media-server
# RUN touch /var/log/hide/hide.log
RUN chown -R www-data:root /var/log/media-server

RUN apt install -y postgresql postgresql-contrib
RUN apt-get install -y redis
RUN apt-get install -y cron
RUN apt-get upgrade -y cron
RUN apt-get install -y ntp
RUN apt-get install -y sudo
RUN apt install -y git

EXPOSE 80
ENTRYPOINT ["/usr/local/media-server/entrypoint.sh"]

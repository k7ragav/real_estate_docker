FROM python:3.8

RUN apt-get update

COPY . /$CONTAINERNAME
WORKDIR /$CONTAINERNAME

RUN pip install -r /$CONTAINERNAME/requirements.txt

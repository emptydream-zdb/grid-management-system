FROM python:3.10.14-slim

WORKDIR /usr/src/app

COPY . .

RUN pip3 install -r requirements.txt
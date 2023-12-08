FROM python:3.11-buster

WORKDIR /app

COPY requirements.txt /app/requirements.txt
COPY GoAlgoMlPart/requirements.txt /app/GoAlgoMlPart/requirements.txt

RUN ["pip3", "install", "-r", "requirements.txt"]
COPY . /app/


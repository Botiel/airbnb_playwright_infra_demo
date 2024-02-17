FROM mcr.microsoft.com/playwright/python:v1.41.0-jammy

WORKDIR /app

RUN apt-get update && apt-get install -y python3.11 python3-pip
RUN python3 -m pip install --upgrade pip
RUN apt-get install vim -y

COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt
RUN playwright install --with-deps

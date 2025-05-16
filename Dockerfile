# syntax=docker/dockerfile:1
FROM nikolaik/python-nodejs:python3.11-nodejs18
# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /code

# Install wget and jq for JSON parsing
RUN apt-get update && apt-get install -y wget jq
RUN apt-get install -y wget unzip libnss3

RUN apt update
RUN apt install gettext -y

# install dependencies
COPY requirements.txt /code/
COPY requirements_test.txt /code/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install -r requirements_test.txt

COPY . /code/

#TODO: Run this line to create image: "docker build -t dpb_p3-11:latest ."
# docker build --progress=plain --no-cache -t dpb_p3-11:latest .

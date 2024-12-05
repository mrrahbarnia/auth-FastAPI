FROM python:3.12-bullseye
LABEL maintainer="mrrahbarnia@gmail.com"

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r /tmp/requirements.txt

RUN apt-get update && \
    apt-get install -y gcc libpq-dev curl && \
    apt clean && \
    rm -rf /tmp

COPY . .

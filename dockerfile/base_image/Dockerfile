FROM docker.arvancloud.ir/python:3.12-alpine

COPY requirements.txt .

LABEL maintainer="mysum325g@gmail.com"

RUN cp /dev/null /etc/apk/repositories && \
    echo "https://mirror.mobinhost.com/alpine/v3.22/main" >> /etc/apk/repositories && \
    echo "https://mirror.mobinhost.com/alpine/v3.22/community" >> /etc/apk/repositories && \
    apk update && \
    apk upgrade && \
    apk add --no-cache bash postgresql16-client curl gcc python3-dev musl-dev linux-headers libpq && \
    pip install --index-url https://mirror-pypi.runflare.com/simple --upgrade pip && \
    pip install --index-url https://mirror-pypi.runflare.com/simple -r requirements.txt \

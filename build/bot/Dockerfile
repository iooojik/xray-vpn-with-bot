FROM python:3.13-alpine

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apk update && apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    jpeg-dev \
    zlib-dev \
    docker-cli \
    make

RUN addgroup -S botgroup && adduser -S bot -G botgroup && chown -R bot:botgroup /app

USER bot

COPY ./src /app/src
COPY ./requirements.txt /app
COPY ./Makefile /app

RUN make prepare

CMD ["make", "run"]

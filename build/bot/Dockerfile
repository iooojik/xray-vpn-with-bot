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

COPY ./src /app/src
COPY ./requirements.txt /app
COPY ./Makefile /app

RUN make prepare

RUN rm -rf requirements.txt

CMD ["make", "run"]

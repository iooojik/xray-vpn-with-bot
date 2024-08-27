FROM python:3.12-alpine

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

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "-m", "src.bot"]

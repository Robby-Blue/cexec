FROM alpine:3.24

WORKDIR /app

RUN apk add uv

COPY client/pyproject.toml .
COPY client/uv.lock .
COPY client/.python-version .

RUN uv sync

COPY version.json .

COPY client .

CMD [ "uv", "run", "python", "-u", "src/main.py" ]
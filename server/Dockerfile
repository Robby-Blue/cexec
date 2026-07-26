FROM alpine:3.24

WORKDIR /app

RUN apk add uv

COPY server/pyproject.toml .
COPY server/uv.lock .
COPY server/.python-version .

RUN uv sync

COPY version.json .

COPY server .

CMD [ "uv", "run", "python", "-u", "backend/main.py" ]
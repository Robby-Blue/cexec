FROM alpine:3.24

WORKDIR /app

RUN apk add uv

COPY pyproject.toml .
COPY uv.lock .
COPY .python-version .

RUN uv sync

COPY . .

CMD [ "uv", "run", "backend/main.py" ]
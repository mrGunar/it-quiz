FROM python:3.12-slim-trixie
RUN set -xe

WORKDIR /quizz

RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin/:$PATH"

ENV UV_NO_DEV=1

COPY pyproject.toml .
RUN uv lock

COPY . .

CMD uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

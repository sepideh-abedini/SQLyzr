FROM python:3.11-slim AS builder
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
  --mount=type=cache,target=/var/lib/apt,sharing=locked \
  apt update && apt-get --no-install-recommends install -y vim jq default-jre curl unzip

RUN curl -L -k -o /tmp/stanford-corenlp.zip http://nlp.stanford.edu/software/stanford-corenlp-full-2018-10-05.zip
RUN unzip /tmp/stanford-corenlp.zip -d /tmp/stanford-corenlp

RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /app

COPY pyproject.toml .

RUN uv sync

FROM node:22-alpine AS node

COPY src/web/ui/package*.json ./

RUN npm install

WORKDIR /app

COPY src/web/ui/ ./

ARG SQLYZR_WEB_PORT
ARG SQLYZR_API_URL
ARG BUILD_VERSION
ENV VITE_BUILD_VERSION=${BUILD_VERSION:0:7}
ENV VITE_API_BASE_URL="${SQLYZR_API_URL}"

RUN npm run build-only


FROM python:3.11-slim

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
  --mount=type=cache,target=/var/lib/apt,sharing=locked \
  apt update && apt-get --no-install-recommends install -y default-jre \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

RUN python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt_tab')"

RUN mkdir -p /app/src/third_party/dail/third_party
COPY --from=builder /tmp/stanford-corenlp /app/src/third_party/dail/third_party

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=0

COPY ./src src
COPY ./scripts scripts
COPY ./main.py .
COPY --from=node /app/dist /app/src/web/ui/dist

ENTRYPOINT ["/app/.venv/bin/python"]

CMD ["src/web/server.py"]

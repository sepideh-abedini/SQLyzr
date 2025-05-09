# syntax=docker/dockerfile:1
FROM python:3.11-slim
RUN apt update && apt install -y --no-install-recommends vim jq default-jre curl unzip nodejs npm
RUN curl -L -o /tmp/stanford-corenlp.zip http://nlp.stanford.edu/software/stanford-corenlp-full-2018-10-05.zip

WORKDIR /app

COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip pip install --no-cache-dir -r requirements.txt

RUN python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt_tab')"

RUN mkdir -p /app/src/third_party/dail/third_party
RUN unzip /tmp/stanford-corenlp.zip -d /app/src/third_party/dail/third_party
RUN rm /tmp/stanford-corenlp.zip

ENV PYTHONPATH=/app


ARG WEB_PORT
ARG WEB_DOMAIN
ENV VITE_API_BASE_URL="http://${WEB_DOMAIN}:${WEB_PORT}"


COPY ./src src
COPY ./scripts scripts

WORKDIR /app/src/web/ui

RUN npm install
RUN npm run build

WORKDIR /app
COPY ./temp.py .

EXPOSE ${WEB_PORT}

ENV PYTHONUNBUFFERED=1

RUN echo WEB_DOMAIN=${WEB_DOMAIN}
ENV WEB_DOMAIN=${WEB_PORT}

RUN echo WEB_PORT=${WEB_PORT}
ENV WEB_PORT=${WEB_PORT}

CMD echo ${WEB_PORT}

CMD flask --debug --app src/web/server.py run -h 0.0.0.0 -p $WEB_PORT

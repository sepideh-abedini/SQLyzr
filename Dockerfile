FROM python:3.11-slim AS builder
RUN apt update && apt install -y --no-install-recommends vim jq default-jre curl unzip

WORKDIR /app

RUN curl -L -o /tmp/stanford-corenlp.zip http://nlp.stanford.edu/software/stanford-corenlp-full-2018-10-05.zip

COPY requirements.txt .
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install -r requirements.txt
RUN mkdir -p /app/src/third_party/dail/third_party
RUN unzip /tmp/stanford-corenlp.zip -d /tmp/stanford-corenlp

FROM node:22-alpine AS node

COPY src/web/ui/package*.json ./

RUN npm install

WORKDIR /app

COPY src/web/ui/ ./

RUN ls

ARG WEB_PORT
ARG WEB_DOMAIN
ENV VITE_API_BASE_URL="http://${WEB_DOMAIN}:${WEB_PORT}"

RUN npm run build

FROM python:3.11-slim 

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt_tab')"

COPY --from=builder /tmp/stanford-corenlp /app/src/third_party/dail/third_party 

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

COPY ./src src
COPY ./scripts scripts
COPY ./main.py .
COPY ./temp.py .
COPY ./scripts/ /usr/local/bin
COPY --from=node /app/dist /app/src/web/ui/dist

ARG WEB_PORT
ENV WEB_PORT=${WEB_PORT}

RUN echo WEB_PORT=$WEB_PORT

RUN chmod +x /usr/local/bin/*.sh
RUN echo 'alias sqlyzr="python3 /app/main.py"' >> ~/.bashrc

CMD flask --debug --app src/web/server.py run -h 0.0.0.0 -p $WEB_PORT

FROM python:3.11-slim
RUN apt update && apt install -y --no-install-recommends vim jq default-jre curl unzip nodejs npm

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt_tab')"

RUN mkdir -p /app/src/third_party/dail/third_party
RUN curl -L -o /tmp/stanford-corenlp.zip http://nlp.stanford.edu/software/stanford-corenlp-full-2018-10-05.zip
RUN unzip /tmp/stanford-corenlp.zip -d /app/src/third_party/dail/third_party
RUN rm /tmp/stanford-corenlp.zip

ENV PYTHONPATH=/app

COPY ./src src
COPY ./scripts scripts

ARG WEB_PORT
ARG WEB_DOMAIN
ENV VITE_API_BASE_URL="http://${WEB_DOMAIN}:${WEB_PORT}"

WORKDIR /app/src/web/ui
RUN npm install
RUN npm run build

WORKDIR /app

EXPOSE ${WEB_PORT}

CMD flask --app src/web/server.py run -h 0.0.0.0 -p ${WEB_PORT}
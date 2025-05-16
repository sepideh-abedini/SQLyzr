FROM python:3.11-slim
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
  --mount=type=cache,target=/var/lib/apt,sharing=locked \
  apt update && apt-get --no-install-recommends install -y vim jq default-jre curl unzip

WORKDIR /app

COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt

RUN python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt_tab')"

RUN mkdir -p /app/src/third_party/dail/third_party
RUN curl -L -o /tmp/stanford-corenlp.zip https://storage.googleapis.com/sepid/cdn/stanford-corenlp-full-2018-10-05.zip
RUN unzip /tmp/stanford-corenlp.zip -d /app/src/third_party/dail/third_party
RUN rm /tmp/stanford-corenlp.zip

ENV PYTHONPATH=/app
ENV TIKTOKEN_CACHE_DIR=/app/tiktoken_cache

RUN python -c "import tiktoken; tiktoken.encoding_for_model('gpt-4o');"
RUN python -c "import tiktoken; tiktoken.encoding_for_model('gpt-4o-mini');"
RUN python -c "import tiktoken; tiktoken.encoding_for_model('gpt-3.5-turbo');"

COPY ./src src
COPY ./scripts scripts
COPY ./main.py .
COPY ./temp.py .
COPY ./scripts/ /usr/local/bin
RUN chmod +x /usr/local/bin/*.sh
RUN echo 'alias sqlyzr="python3 /app/main.py"' >> ~/.bashrc
RUN echo 'alias e2e="python3 /app/e2e.py"' >> ~/.bashrc

ENTRYPOINT ["bash"]



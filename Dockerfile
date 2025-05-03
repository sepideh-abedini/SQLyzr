FROM python:3.11-slim
RUN apt update && apt install -y --no-install-recommends vim jq default-jre curl unzip

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
COPY ./main.py .
COPY ./scripts/ /usr/local/bin
RUN chmod +x /usr/local/bin/*.sh
RUN echo 'alias sqlyzr="python3 /app/main.py"' >> ~/.bashrc
RUN echo 'alias e2e="python3 /app/e2e.py"' >> ~/.bashrc

ENTRYPOINT ["bash"]



FROM python:3.11-slim
RUN apt update && apt install -y --no-install-recommends vim jq default-jre

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt_tab')"

ENV PYTHONPATH=/app

COPY ./src src
COPY ./scripts scripts
COPY ./main.py .
COPY ./scripts/ /usr/local/bin
RUN chmod +x /usr/local/bin/*.sh
RUN echo 'alias sqlyzr="python3 /app/main.py"' >> ~/.bashrc
RUN echo 'alias e2e="python3 /app/e2e.py"' >> ~/.bashrc

ENTRYPOINT ["bash"]



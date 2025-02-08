FROM python:3.11
RUN apt update && apt install -y --no-install-recommends vim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -c "import nltk; nltk.download('stopwords')"

ENV PYTHONPATH=.

COPY ./src src
COPY ./main.py .

ENTRYPOINT ["bash"]



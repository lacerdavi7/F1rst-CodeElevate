FROM python:3.10-slim

WORKDIR /app

RUN pip install faker kafka-python psycopg2-binary

COPY producer.py .

CMD ["python", "producer.py"]
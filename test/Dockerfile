FROM python:3.10.18-slim

# Instala dependências básicas
RUN apt-get update && apt-get install -y openjdk-21-jre-headless git curl && rm -rf /var/lib/apt/lists/*

# Variáveis de ambiente para PySpark
ENV JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH

# Instala PySpark, pytest e outras libs
RUN pip install --no-cache-dir pyspark pytest faker kafka-python psycopg2-binary

# Cria diretório de trabalho
WORKDIR /app

# Copia código fonte e testes
COPY ./src /app/src
COPY ./src/tests /app/src/tests

# Define comando padrão (rodar pytest)
CMD ["pytest", "-v", "/app/src/tests"]

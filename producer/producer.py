import os
import time
import json
from faker import Faker
from kafka import KafkaProducer

fake = Faker()

KAFKA_BOOTSTRAP_SERVERS = "kafka:9092"
KAFKA_TOPIC = "iot_sensor"

# Cria produtor
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

print(f"Produzindo mensagens para {KAFKA_TOPIC} no broker {KAFKA_BOOTSTRAP_SERVERS} ...")

# Tempo inicial
start_time = time.time()
minutos = 5
duration = minutos * 60

try:
    while (time.time() - start_time) < duration:
        data = {
            "id_sensor": fake.uuid4(),
            "temperatura": round(fake.pyfloat(min_value=18, max_value=35), 2),
            "umidade": round(fake.pyfloat(min_value=30, max_value=90), 2),
            "dthr_medicao": fake.iso8601()
        }

        # Envia para o Kafka
        future = producer.send(KAFKA_TOPIC, value=data)

        # Aguarda confirmação
        result = future.get(timeout=10)
        print(f"Enviado: {data} para {result.topic} [partição {result.partition}]")

        time.sleep(1)

    print(f"{minutos} minutos se passaram. Encerrando produtor.")

except KeyboardInterrupt:
    print("Produção interrompida pelo usuário.")

finally:
    producer.close()

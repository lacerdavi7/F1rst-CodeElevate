from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StringType, IntegerType, FloatType, TimestampType


# Config Kafka
KAFKA_BOOTSTRAP_SERVERS = "kafka:9092"
KAFKA_TOPIC = "iot_sensor"
CHECKPOINT = "/opt/spark/checkpoints/kafka_to_pg"

# Config Postgres
jdbc_url = "jdbc:postgresql://postgres:5432/sparkdb"
jdbc_props = {
    "driver": "org.postgresql.Driver",
    "user": "sparkuser",
    "password": "sparkpass",
    "stringtype": "unspecified"  # evita alguns issues com tipos
}
table = "medicao_sensores"

spark = SparkSession.builder.appName("read_test_straeam").getOrCreate()


spark.sparkContext.setLogLevel("WARN")

# funções
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS) \
    .option("subscribe", KAFKA_TOPIC) \
    .option("startingOffsets", "earliest") \
    .load()

def write_with_retry(batch_df, batch_id, max_retries=5):
    if batch_df.rdd.isEmpty():
        return
    for attempt in range(max_retries):
        try:
            (batch_df
             .write
             .mode("append")
             .jdbc(jdbc_url, table, properties=jdbc_props))
            return
        except Exception as e:
            if attempt == max_retries - 1:
                # Deixa a exceção subir para o Spark marcar erro no micro-batch
                raise
            time.sleep(2 ** attempt)  # backoff exponencial

# program

schema = StructType() \
    .add("id_sensor", StringType()) \
    .add("temperatura", FloatType())\
    .add("umidade", FloatType())\
    .add("dthr_medicao", TimestampType())


parsed_df = df.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select("data.*")


query = (parsed_df
    .writeStream
    .foreachBatch(write_with_retry)
    .option("checkpointLocation", CHECKPOINT)
    .trigger(processingTime="20 seconds")
    .start())

query.awaitTermination()

spark.stop()
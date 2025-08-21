build:
	docker compose build

down:
	docker compose down --volumes --remove-orphans

run:
	make down && docker compose up

create-topic:
	docker exec -it f1rst-codeelevate-kafka-1 kafka-topics.sh --create --bootstrap-server localhost:9092 --topic iot_sensor

stream:
	docker exec -it f1rst-codeelevate-spark-1 spark-submit --master local[*] --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0,org.postgresql:postgresql:42.7.3 /src/stream_iot_sensor.py

batch:
	docker exec -it f1rst-codeelevate-spark-1 spark-submit --master local[*] --packages org.postgresql:postgresql:42.7.3 /src/batch_job.py

iot-sensor:
	docker-compose up -d producer

unit-test:
	docker exec -it f1rst-codeelevate-pyspark-tests-1 bash -c "PYTHONPATH=/app pytest -v /app/src/tests"

postgres:
	docker exec -it f1rst-codeelevate-postgres-1 psql -U sparkuser -d sparkdb
```sh
docker exec -it ml_infra_kafka_1 bash
cd /opt/kafka
bin/kafka-topics.sh --bootstrap-server kafka:9092 --list 
bin/kafka-topics.sh --bootstrap-server kafka:9092 --describe --topic infer_serv
bin/kafka-console-consumer.sh --bootstrap-server kafka:9092 --from-beginning --topic infer_serv
```
from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    #bootstrap_servers='kafka:9092',
    bootstrap_servers='localhost:9093',
    group_id='group_1',
    enable_auto_commit=True,
    auto_commit_interval_ms=1000,
    #value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )

consumer.subscribe(['infer_serv'])

for message in consumer:
    # process the message here
    print(message.value.decode('utf-8'))
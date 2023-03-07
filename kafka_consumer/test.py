import logging
from bson.objectid import ObjectId
import pymongo
import yaml
import kafka
from datetime import datetime as dt
import sys
import json

producer = kafka.KafkaProducer(
    bootstrap_servers=['localhost:9093'], 
    value_serializer=lambda m: bytes(m, 'utf-8'))

kafka_topic = 'infer_serv'
producer.send(kafka_topic, "Hello, Kafka!")
producer.flush()
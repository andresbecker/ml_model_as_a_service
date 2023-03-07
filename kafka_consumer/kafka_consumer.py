from kafka import KafkaConsumer
import json
from PIL import Image
import base64
from io import BytesIO
import tensorflow as tf
from tensorflow.keras.applications.imagenet_utils import preprocess_input, decode_predictions
import numpy as np
import logging
import requests

def _prepare_image(encoded_img, img_size=(299,299)):
    """
    Decode (from Base 64) and transform it into a (1,299,299,3) numpy array
    Input: str, Base64 encoded image
    Output: numpy array
    """
    logger.debug(f"Encoded: {encoded_img[0:10]}...{encoded_img[-10:]}")
    # Decode image
    decoded_img = base64.b64decode(encoded_img)
    logger.debug(f"Decoded: {decoded_img[0:10]}...{decoded_img[-10:]}")
    # Convert image into an array
    img = Image.open(BytesIO(decoded_img))
    img = img.convert('RGB')
    img = np.asarray(img)
    # Add batch dimension
    img = np.expand_dims(img, axis=0)
    # Resize and preprocess image
    img = tf.image.resize(img, img_size)
    img = preprocess_input(img)
    
    # return image as numpy array
    return img.numpy()

# Set logger to log into disk file
# Create a logger
logger = logging.getLogger("kafka_consumer")
# Set the logging level
logger.setLevel(logging.DEBUG)
# Set logger handler
handler = logging.FileHandler("../logs/kafka_consumer.log")
# Set the logging format
formatter = logging.Formatter('%(asctime)s: %(name)s: %(levelname)s: %(message)s','%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)
# Add handler to logger
logger.addHandler(handler)

# Log a message
# logger.[debug,info,warning,error,critical]("This is a message")
# logger.debug("This is a message")

consumer = KafkaConsumer(
    #bootstrap_servers='kafka:9092',
    bootstrap_servers='localhost:9093',
    group_id='group_1',
    enable_auto_commit=True,
    auto_commit_interval_ms=1000,
    #value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )

# Subscribe to the Kafka topic to consume messages
consumer.subscribe(['infer_serv'])

model_name = 'xception_classification'
url = 'http://localhost:8501/v1/models/' + model_name + ':predict'

for message in consumer:
    # process the message here
    kafka_msg = message.value.decode('utf-8')
    kafka_msg = json.loads(kafka_msg)
    
    logger.debug(kafka_msg)
    
    if kafka_msg['job_status'] == "RUNNING" and kafka_msg['img'] != 'null':

        img = _prepare_image(kafka_msg['img'])
        logger.debug(img.shape)

        payload = {
            "instances": img.tolist()
        }
        response = requests.post(url, json=payload)
        predictions = np.array(response.json()['predictions'])
        predicted_label = decode_predictions(predictions, top=1)[0][0][1]
        label_prob = decode_predictions(predictions, top=1)[0][0][2]

        logger.debug(f"Predicted label: {predicted_label}, Label prob: {label_prob}")
        print(f"Predicted label: {predicted_label}, Label prob: {label_prob}")






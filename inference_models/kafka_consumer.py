from kafka import KafkaConsumer
import json
from PIL import Image
import base64
from io import BytesIO
import tensorflow as tf
from tensorflow.keras.applications.imagenet_utils import preprocess_input

def _prepare_image(encoded_img, img_size=(299,299)):
    print(len(encoded_img), encoded_img[0:10], encoded_img[-10:])
    # Decode image
    decoded_img = base64.b64decode(encoded_img)
    print(len(decoded_img), decoded_img[0:10], encoded_img[-10:])
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
    kafka_msg = message.value.decode('utf-8')
    kafka_msg = json.loads(kafka_msg)
    print(kafka_msg)
    if 'img' in kafka_msg.keys():
        img = kafka_msg['img']
        img = _prepare_image(img)
        print(img.shape)

    # Issue: image in base 64 encoding is read as string and not as binary, which is causing the issue. However, time is up....
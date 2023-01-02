import logging
import connexion
import pymongo
import kafka 


def list_inference_jobs():
    pass

def create_inference_job():
    pass

def get_inference_job():
    pass

def delete_inference_job():
    pass

def execute_inference_job():
    pass

def get_inference_job_result():
    pass


logging.basicConfig(level=logging.INFO)
mongo_client = pymongo.MongoClient("mongodb://mongodb:27017/")
db = mongo_client["inference"]
jobs = db["jobs"]

producer = kafka.KafkaProducer(bootstrap_servers=['kafka:9092'])

app = connexion.FlaskApp(__name__)
app.add_api("openapi.yml")
application = app.app

if __name__ == "__main__":
    app.run(port=8080, use_reloader=False, threaded=False)
    
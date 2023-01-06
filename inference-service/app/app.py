import logging
import connexion
from bson.objectid import ObjectId
import pymongo
import yaml
#import kafka

sample_job = {
    'jobs': [
        {
            'id': 'x1', 
            'name': 'Test inf job',
            'status': 'NEW',
            'type': 'CLASSIFICATION'
        },
        {
            'id': 'x2', 
            'name': 'Test inf job no. 2',
            'status': 'CANCELLED',
            'type': 'OBJECT_DETECTION'
        }
    ]
}

def list_inference_jobs():
    return sample_job

def create_inference_job():
    
    # Generate Json to be inserted into MongoDB base on the user request
    req_json = {key: connexion.request.json[key] for key in job_prop.keys() if key in connexion.request.json.keys()}

    # Insert job into MongoDB inference.jobs collection
    jobs.insert_one(req_json)
    # get job id and store it in the dic as str
    req_json['id'] = str(req_json['_id'])

    logger.debug(req_json)

    # Return only the properties defined on the api job schema
    return {key: req_json[key] for key in job_prop.keys() if key in req_json.keys()}

def get_inference_job():
    pass

def delete_inference_job():
    pass

def execute_inference_job():
    pass

def get_inference_job_result():
    pass

# Set logging
# Create a logger
logger = logging.getLogger("infer_serv")
# Set the logging level
logger.setLevel(logging.DEBUG)
# Send logs to a file
handler = logging.FileHandler("./logs/celo_chl.log")
# Set the logging format
formatter = logging.Formatter("%(asctime)s: %(name)s: %(levelname)s: %(message)s","%Y-%m-%d %H:%M:%S")
handler.setFormatter(formatter)
# Add the handler to the logger
logger.addHandler(handler)
# Log a message
# logger.[debug,info,warning,error,critical]("This is a message")

#logging.basicConfig(level=logging.INFO)
mongo_client = pymongo.MongoClient("mongodb://mongodb:27017/")
db = mongo_client["inference"]
jobs = db["jobs"]

#producer = kafka.KafkaProducer(bootstrap_servers=['kafka:9092'])

app = connexion.FlaskApp(__name__)
app.add_api("openapi.yml")
application = app.app

# Load api definition as a dictionary
with open("./openapi.yml", 'r') as file:
    try:
        api_def = yaml.safe_load(file)
    except yaml.YAMLError as exc:
        logger.error(exc)
job_prop = api_def['components']['schemas']['Job']['properties']

if __name__ == "__main__":
    app.run(port=8080, use_reloader=False, threaded=False)
    
import logging
import connexion
from bson.objectid import ObjectId
import pymongo
import yaml
import kafka

class KafkaHandler(logging.Handler):
    def emit(self, record):
        producer.send(kafka_topic, self.format(record))
        producer.flush()

def _find_job(id: str):
    """
    Returns a job from the collection. This function is meant to handle the case when a 
    non-valid ObjectId is provided.
    input: id as string
    output: a job as dictionary if id is a valid object id and exist in the collection. None otherwise 
    """
    # Retrieve job from collection
    try:
        job = jobs.find_one({'_id': ObjectId(id)})
    except:
        # if the provided id is not a valid ObjectId, then set job as None
        job = None

    return job

def list_inference_jobs():

    logger.debug("Inference jobs listed")

    # Retrieve all documents from the jobs collection
    # TODO: do something to avoid dumping the whole collection without affecting the functionality
    job_collec = jobs.find({}).limit(max_n_jobs)

    # Rename and reformat job id and show only the properties defined on the api definition
    jobs_list = []
    for job in job_collec:
        job['id'] = str(job['_id'])
        jobs_list.append({key: job[key] for key in job_prop.keys() if key in job.keys()})

    # Return only the first thousand jobs
    return jobs_list, 200

def create_inference_job():

    # Generate Json to be inserted into MongoDB base on the user request
    req_json = {key: connexion.request.json[key] for key in job_prop.keys() if key in connexion.request.json.keys()}
    # Ignore id provided by the user
    try:
        del(req_json['id'])
    except:
        pass

    # TODO: add mechanism to write into the collection jobs with status=NEW

    # Insert job into MongoDB inference.jobs collection
    jobs.insert_one(req_json)
    # get job id and store it in the dic as str
    req_json['id'] = str(req_json['_id'])

    logger.info(f"Inference job created with id: {req_json['id']}")

    # Return only the properties defined on the api job schema
    return {key: req_json[key] for key in job_prop.keys() if key in req_json.keys()}, 201

def get_inference_job(id: str):

    # Look for job
    job = _find_job(id)

    # Return 404 if job could not be found
    if job is None:
        logger.warning(f"Inference job with id: {id} not found")
        return {}, 404

    logger.debug(f"Inference job with id: {id} information retrieved")

    # Add/rename job id
    job['id'] = str(job['_id'])

    # Return only the properties defined on the api job schema
    return  {key: job[key] for key in job_prop.keys() if key in job.keys()}, 200

def delete_inference_job(id: str):

    # Look for job
    job = _find_job(id)

    # Return 404 if job could not be found
    if job is None:
        logger.warning(f"Inference job with id: {id} requested to be deleted, but id not found")
        return {}, 404

    # Remove job from collection
    jobs.delete_one({'_id': ObjectId(id)})
    
    logger.info(f"Inference job with id: {id} deleted")

    return '', 204
    
def execute_inference_job():
    pass

def get_inference_job_result():
    pass

# Set kafka producer client
producer = kafka.KafkaProducer(
    bootstrap_servers=['kafka:9092'], 
    value_serializer=lambda v: v.encode('utf-8'))
# Set kafka topic name
kafka_topic = 'infer_serv'

# Set logger to log into Kafka
# Create a logger
logger = logging.getLogger(kafka_topic + '_api')
# Set the logging level
logger.setLevel(logging.DEBUG)
# Set custom Kafka logging handler
handler = KafkaHandler()
# Set the logging format
formatter = logging.Formatter('%(asctime)s: %(name)s: %(levelname)s: %(message)s','%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)
# Add the handler to the logger
logger.addHandler(handler)

# Set logger to log into disk file
# Create a logger
#handler = logging.FileHandler("./logs/celo_chl.log")
# Set the logging format
#handler.setFormatter(formatter)
# Add handler to logger
#logger.addHandler(KafkaLogHandler())

# Log a message
# logger.[debug,info,warning,error,critical]("This is a message")

mongo_client = pymongo.MongoClient("mongodb://mongodb:27017/")
db = mongo_client["inference"]
jobs = db["jobs"]
max_n_jobs = 1000

app = connexion.FlaskApp(__name__)
app.add_api("openapi.yml", validate_responses=True)
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
    
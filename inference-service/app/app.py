import logging
import connexion
from bson.objectid import ObjectId
import pymongo
import yaml
import kafka
from datetime import datetime as dt
import sys
import json

def _create_kafka_event(request_rc=200, job_id='null', img='null'):
    """
    Create an event on kafka that complies with the CloudEvents 1.0 specification.
    This function collects information about the function corresponding to an 
    operationId defined on the OpenAPI specification. Do not call this function 
    unless it is done from a function corresponding to operationId on the OpenAPI 
    specification. 
    input:
        request_rc: int, http request return code
        job_id: str, job id if applicable, otherwise 'null'
    output: None 
    """
    op_name = "app." + sys._getframe(1).f_code.co_name

    op_info = None
    for path in api_def['paths'].keys():
        for r_meth in api_def['paths'][path].keys():
            if op_name == api_def['paths'][path][r_meth]['operationId']:
                op_info = {
                    "operationId": op_name, 
                    "path": path, 
                    "request_method": r_meth, 
                    "request_rc": str(request_rc),
                    "job_id": job_id,
                    "img": img}

    if op_info is None:
        raise Exception(f'operationId not {op_name} found in the OpenAPI definition!')

    event = {
        "specversion" : "1.0",
        "time": dt.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    #producer.send(kafka_topic, bytes(str({**event, **op_info}), 'utf-8'))
    producer.send(kafka_topic, json.dumps({**event, **op_info}))
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

    # Retrieve all documents from the jobs collection
    # TODO: do something to avoid dumping the whole collection without affecting the functionality
    job_collec = jobs.find({}).limit(max_n_jobs)

    # Rename and reformat job id and show only the properties defined on the api definition
    jobs_list = []
    for job in job_collec:
        job['id'] = str(job['_id'])
        jobs_list.append({key: job[key] for key in job_prop.keys() if key in job.keys()})

    # Create kafka event
    _create_kafka_event()

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

    # Create kafka event
    _create_kafka_event(201, req_json['id'])

    # Return only the properties defined on the api job schema
    return {key: req_json[key] for key in job_prop.keys() if key in req_json.keys()}, 201

def get_inference_job(id: str):

    # Look for job
    job = _find_job(id)

    # Return 404 if job could not be found
    if job is None:
        # Create kafka event
        _create_kafka_event(404, id)
        return {}, 404

    # Add/rename job id
    job['id'] = str(job['_id'])

    # Create kafka event
    _create_kafka_event(200, id)

    # Return only the properties defined on the api job schema
    return  {key: job[key] for key in job_prop.keys() if key in job.keys()}, 200

def delete_inference_job(id: str):

    # Look for job
    job = _find_job(id)

    # Return 404 if job could not be found
    if job is None:
        # Create kafka event
        _create_kafka_event(404, id)
        return {}, 404

    # Remove job from collection
    jobs.delete_one({'_id': ObjectId(id)})
    
    # Create kafka event
    _create_kafka_event(204, id)

    return '', 204
    
def execute_inference_job(id: str):

    # Look for job
    job = _find_job(id)

    # Return 404 if job could not be found
    if job is None:
        # Create kafka event
        return {}, 404

    # Add/rename job id
    job['id'] = str(job['_id'])

    # Load image sended on the payload
    req_json = connexion.request.json
    if 'image/jpeg' in req_json.keys() and 'image/png' in req_json.keys():
        err_msg = "Inference job execution failed, jpeg and png images provided! please specify only one"
        logger.error(err_msg)
        return {"error": err_msg}, 500

    elif 'image/jpeg' in req_json.keys():
        img = req_json['image/jpeg']

    elif 'image/png' in req_json.keys():
        img = req_json['image/png']

    else:
        err_msg = "Inference job execution failed, jpeg or png image not provided!"
        logger.error(err_msg)
        return {"error": err_msg}, 500

    # Create kafka event
    _create_kafka_event(200, id, img)

    # Return only the properties defined on the api job schema
    return  {key: job[key] for key in job_prop.keys() if key in job.keys()}, 200

def get_inference_job_result():
    pass

# Set kafka producer client
#producer = kafka.KafkaProducer(bootstrap_servers=['kafka:9092'])

producer = kafka.KafkaProducer(
    bootstrap_servers=['kafka:9092'], 
    value_serializer=lambda m: bytes(m, 'utf-8'))

#bytes(json.dumps({**event, **op_info}), 'utf-8')

# Set kafka topic name
kafka_topic = 'infer_serv'
#producer.send(kafka_topic, b"Hello, Kafka!")
#producer.flush()


# Set logger to log into disk file
# Create a logger
logger = logging.getLogger(kafka_topic + '_api')
# Set the logging level
logger.setLevel(logging.DEBUG)
# Set logger handler
handler = logging.FileHandler("./logs/celo_chl.log")
# Set the logging format
formatter = logging.Formatter('%(asctime)s: %(name)s: %(levelname)s: %(message)s','%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)
# Add handler to logger
logger.addHandler(handler)

# Log a message
# logger.[debug,info,warning,error,critical]("This is a message")
# logger.debug("This is a message")

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
    
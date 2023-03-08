## Install docker and docker-compose
```sh
sudo apt update
sudo apt install docker docker-compose

# Allow docker containers to be started without sudo (subsecuent logout and login needed)
sudo usermod -aG docker $USER
```

Create a local environment for development and testing
```sh
python3 -m pip install virtualenv
python3 -m venv ~/.venv/mlops
source ~/.venv/mlops/bin/activate
python3 -m pip install gunicorn pymongo kafka-python connexion[swagger-ui]

# Start web-server
gunicorn --bind 0.0.0.0:8080 app:app
```

Docker useful commands
```sh
# Celan build cache
docker builder prune

docker-compose down
docker-compose up --build -d

docker exec -it ml_infra_inference_1 bash

docker-compose logs
```



# TODOs
* Validate that jobs are unique under name, status and type
* Make MongoDB and Kafka container restart persistent
* Improve `list_inference_jobs` to be more flexible regarding the number of records it returns 
* Implement security on the Databases! everybody can write and read from them!
* Apparently the response validation in connection does not work as expected (https://connexion.readthedocs.io/en/latest/response.html)
* Init collection to avoid errors if you try to retrieve a job with id and the collection does not exist
* Update diagram
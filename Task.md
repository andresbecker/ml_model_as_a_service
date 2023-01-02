# CeloAi ML infra Programming Challenge


## Main Goal
Implement an architecture that allows clients to run multiple computer vision inference jobs and receive the results in event driven fashion.

🚨 You are free to choose any programming language and database technology. 
The final solution must cover all task requirements and run by a `docker-compose.yaml` file.

## Get the sample application "Up and Running"

The sample application is a very simple microservice that manages inference jobs. The service is "dockerized" and comes with a [docker-compose file](docker-compose.yaml) that helps you set it up quickly. 
You start the application with `docker-compose up -d`. This will create the following setup:

![Basic Architecture](assets/basic.svg)

The Application exposes a REST API that is described with an [OpenAPI 3.0 compliant specification](inference-service/openapi.yaml). This specification is available on the running service under [/api/v1/inference/ui/](http://127.0.0.1:8080/api/v1/inference/ui/).

## Task 1: Implement inference service
The inference service is built using [connexion](https://connexion.readthedocs.io/en/latest/) which follows the API first engineering principle and therefore  automatically handles HTTP requests defined using the provided [OpenAPI specification](inference-service/openapi.yaml).

- Take a look at the specification and think about the provided API. 
Is it complete? Does it follow RESTful guidelines and best practices?
If necessary, update the specification.
- Provide an implementation that integrates the service with MongoDB 
- Integrate Kafka for each operation on an "Inference Job" entity that makes sense to you, which should result in the creation of a [CloudEvents 1.0](https://github.com/cloudevents/spec/blob/v1.0.1/json-format.md) compliant message in Kafka.

Once you have completed these tasks, you should use the API to create, delete, and execute inference jobs. 
You can ssh into the Kafka container (`docker exec ...`) and use the native Kafka scripts to print the event log contained within your topics. 
The scripts are located in `/opt/bitnami/kafka/bin`. 
Remember that inside the container your bootstrap server is `kafka:9092` and on your laptop it is `localhost:9093`.

Example commands:
- bin/kafka-topics.sh --bootstrap-server kafka:9092 --list 
- bin/kafka-topics.sh --bootstrap-server kafka:9092 --describe --topic <\topic-name>
- bin/kafka-console-consumer.sh --bootstrap-server kafka:9092 --from-beginning --topic <\topic-name>

## Task 2: Create a new service to execute inference jobs 

Now it is your time to design and develop a service from scratch and to integrate it into the existing landscape.
Whilst you are entirely free in your technology choices (databases, frameworks, languages, etc.), we want your service to fulfill the following criteria:

- Subscribe to events for necessary operations emitted by the existing Kafka Broker 
- Publish events for necessary operations to the existing Kafka Broker (events should follow the [CloudEvents 1.0 spec](https://github.com/cloudevents/spec/blob/v1.0.1/json-format.md))
- The service must at least be able to run inference on two different computer vision models, e.g. image classification and object detection
  - You are free to use any framework of your choice
  - Our recommendation:
    - [tflite](https://www.tensorflow.org/lite): checkout the [quickstart](https://www.tensorflow.org/lite/guide/python#install_tensorflow_lite_for_python)
    - download pre-trained models from [TensorFlow Hub](https://tfhub.dev/s?deployment-format=lite&module-type=image-classification,image-object-detection)

In order to not overcomplicate things:
* You don't need to do excessive data preprocessing and error handling. However please explain where you compromised and how you would do it properly
* If you think certain ideas are too much effort to implement, just explain them 

## Task 3: Get inference job results

At the moment the user can create, execute and delete inference jobs. 
Now he should be able to read the results of the inference jobs as well.
You are entirely free to design and implement this functionality.

After you have implemented the functionality, take a step back and think about the implementation. 
- What were tradeoff decisions you had to take? 
- What are potential security issues? 
- What do they mean to things like scalability, performance, consistency, ...?
- Would there be better designs to achieve the same goal (if you would have had more time)?

## Task 4: Simulation of traffic

Now the application is ready and waiting for some action. 
Since you are a backend engineer, we don't ask you to create a Web UI. 
However, you should create a script that can be used to simulate multiple inference jobs triggered by your client. 
You can find some sample images in the [`assets/test_data`](assets/test_data) folder.
A jupyter notebook would be fine as well.

(Optional) The script should also have a mode that logs out changes to the respective entities (sourced from kafka). 
The log should continuously stream data in a human-readable format (e.g. `Inference job (id: <abc>) <type>: <status>`). 

## Task 5: Presentation

Congratulations you have completed the technical part of your challenge. Now you need to sell it to us. 
For that we would expect the following to be handed in once your deadline is expired:

* Markdown summary highlighting: 
  - Architecture ([original architecture is available as drawio](assets/Architecture.drawio))
  - choices made and reasons (language, database, etc.)
  - proposed improvements, what worked and what not
  - how you would propose to handle security
* Complete Source Code 
* Amended docker-compose file

**Please send back your solution as git repository (including .git folder) packed as zip archive.**

During the meeting we would follow the below structure:

* Demo of your Solution:
  * Provide a script that shows the various operations (also log out the event stream)
* Joint discussion of your previously handed-in summary document
* Presentation of your source code structure with questions and answers
* Open questions that will mainly ask you for reasons of choices you made (language, database, framework, etc.). It is very important to be honest here. If you picked Java as a language because it is the only one you know, don't make up things just say it. 

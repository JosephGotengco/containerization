import connexion
from connexion import NoContent
import os
import json
import requests
import yaml
import logging
import logging.config
from apscheduler.schedulers.background import BackgroundScheduler
import datetime
from pykafka import KafkaClient
from flask_cors import CORS, cross_origin

MAX_EVENTS = 10
LOG_FILE = 'events.json'

# load config
with open('app_conf.yaml', 'r') as f:
    app_config = yaml.safe_load(f.read())

events = app_config['events']
kafka_server = events['hostname']
kafka_port = events['port']
kafka_topic = events['topic']

# configure logging
with open('log_conf.yaml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')


def add_fact(body):
    """ Passes add fact request data to database service """

    # LAB 7 CODE
    client = KafkaClient(hosts='{}:{}'.format(kafka_server, kafka_port))
    topic = client.topics[kafka_topic]
    producer = topic.get_sync_producer()

    msg = {
        "type": "ADD FACT",
        "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "payload": body
    }

    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    return NoContent, 201


def subscribe_user(body):
    """ Passes subscibe user request data to database service """

    # LAB 7 CODE
    client = KafkaClient(hosts='{}:{}'.format(kafka_server, kafka_port))
    topic = client.topics[kafka_topic]
    producer = topic.get_sync_producer()

    msg = {
        "type": "ADD USER",
        "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "payload": body
    }

    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    return NoContent, 201


app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("openapi.yaml", base_path='/',
            strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8080)

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

MAX_EVENTS = 10
LOG_FILE = 'events.json'

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yaml"
    log_conf_file = "/config/log_conf.yaml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yaml"
    log_conf_file = "log_conf.yaml"

# load config
with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())

# configure logging
with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

events = app_config['events']
kafka_server = events['hostname']
kafka_port = events['port']
kafka_topic = events['topic']

logger = logging.getLogger('basicLogger')

logger.info("App Conf File: {}".format(app_conf_file))
logger.info("Log Conf File: {}".format(log_conf_file))


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
app.add_api("openapi.yaml", base_path='/',
            strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8080)

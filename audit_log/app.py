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

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yaml"
    log_conf_file = "/config/log_conf.yaml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"

# load config
with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())

# configure logging
with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

logger.info("App Conf File: {}".format(app_conf_file))
logger.info("Log Conf File: {}".format(log_conf_file))


def get_fact(index):
    """ get fact in History """
    hostname = "{}:{}".format(
        app_config["events"]["hostname"],
        app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[app_config["events"]["topic"]]

    consumer = topic.get_simple_consumer(
        reset_offset_on_start=True,
        consumer_timeout_ms=500)

    logger.info("Retrieving fact at index {}".format(index))
    count = 0
    for msg in consumer:
        msg_str = msg.value.decode("utf-8")
        msg = json.loads(msg_str)
        if msg["type"] == "ADD FACT":
            if count == index:
                return msg, 200
            count += 1

    logger.error("Could not find fact at index {}".format(index))

    return {"message": "Not Found"}, 404


def get_user(index):
    """ get user in History """
    hostname = "{}:{}".format(
        app_config["events"]["hostname"],
        app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[app_config["events"]["topic"]]

    consumer = topic.get_simple_consumer(
        reset_offset_on_start=True,
        consumer_timeout_ms=500)

    logger.info("Retrieving fact at index {}".format(index))
    count = 0
    for msg in consumer:
        msg_str = msg.value.decode("utf-8")
        msg = json.loads(msg_str)
        if msg["type"] == "ADD USER":
            if count == index:
                return msg, 200
            count += 1

    logger.error("Could not find fact at index {}".format(index))

    return {"message": "Not Found"}, 404


app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("openapi.yaml", base_path='/',
            strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=9999)

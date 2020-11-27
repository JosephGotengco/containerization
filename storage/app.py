import connexion
from connexion import NoContent
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from interesting_fact import InterestingFact
from user import User
import datetime
import yaml
import logging
import logging.config
import mysql.connector
import pymysql
import json
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread
import os

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

logger = logging.getLogger('basicLogger')

logger.info("App Conf File: {}".format(app_conf_file))
logger.info("Log Conf File: {}".format(log_conf_file))

datastore = app_config["datastore"]
zookeeper = "kafka-service-based.westus2.cloudapp.azure.com:9092"

DB_ENGINE = create_engine(
    "mysql+pymysql://{}:{}@{}:{}/{}".format(datastore["user"], datastore["password"], datastore["hostname"], datastore["port"], datastore["db"]))
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)
logger.info("Connecting to DB. Hostname:{}, Port:{}".format(
    datastore["hostname"], datastore["port"]))
### Facts ###


def get_facts(timestamp):
    """ Gets newly added facts after the timestamp """

    session = DB_SESSION()

    timestamp_datetime = datetime.datetime.strptime(
        timestamp, '%Y-%m-%dT%H:%M:%SZ')

    facts = session.query(InterestingFact).filter(
        InterestingFact.date_added >= timestamp_datetime)

    results_list = []

    for fact in facts:
        results_list.append(fact.to_dict())

    session.close()

    logger.info("Query for Interesting Facts after {} returns {} results".format(
        timestamp, len(results_list)))

    return results_list, 200

### Users ###


def get_subscribers(timestamp):
    """ Gets newly added facts after the timestamp """

    session = DB_SESSION()

    timestamp_datetime = datetime.datetime.strptime(
        timestamp, '%Y-%m-%dT%H:%M:%SZ')

    users = session.query(User).filter(
        User.date_created >= timestamp_datetime)

    results_list = []

    for user in users:
        results_list.append(user.to_dict())

    session.close()

    logger.info("Query for Users after {} returns {} results".format(
        timestamp, len(results_list)))

    return results_list, 200

# LAB 7 CODE


def process_messages():
    """ Process event messages """
    hostname = "{}:{}".format(
        app_config["events"]["hostname"],
        app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[app_config["events"]["topic"]]

    # consume messages on start, don't consume previous ones
    consumer = topic.get_balanced_consumer(
        consumer_group="event_group",
        zookeeper_connect=zookeeper,
        reset_offset_on_start=False,
        auto_commit_enable=True,
        auto_commit_interval=100)

    # this is block - it will wait for new messages
    for msg in consumer:
        msg_str = msg.value.decode("utf-8")
        msg = json.loads(msg_str)
        logger.info("Message: {}".format(msg))

        payload = msg["payload"]

        if msg["type"] == "ADD FACT":
            # STORE ADD FACT
            """ Stores fact into mysql database """

            EVENT_NAME = 'ADD FACT'
            # make unique id upon request
            unique_id = payload['fact_id']

            # create db session
            session = DB_SESSION()

            # create InterestingFact object
            itr_fact = InterestingFact(payload['fact_id'],
                                       payload['user_id'],
                                       payload['fact'],
                                       payload['tags'],
                                       payload['timestamp'])

            # add fact to database
            session.add(itr_fact)
            # commit and close session
            session.commit()
            session.close()

            # log after changes were committed
            stored_log_msg = 'Stored event {} request with a unique id of {}'.format(
                EVENT_NAME, unique_id)
            logger.debug(stored_log_msg)
        elif msg["type"] == "ADD USER":
            # STORE USER
            EVENT_NAME = 'ADD USER'
            # make unique id upon request
            unique_id = payload['user_id']

            # create db session
            session = DB_SESSION()
            # create User object
            user = User(payload['user_id'],
                        payload['username'],
                        payload['subscribed'],
                        payload['timestamp'])

            # add user to database
            session.add(user)
            # commit and close session
            session.commit()
            session.close()

            # log after changes were committed
            stored_log_msg = 'Stored event {} request with a unique id of {}'.format(
                EVENT_NAME, unique_id)
            logger.debug(stored_log_msg)

        # prevent re-read of events
        consumer.commit_offsets()


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", strict_validation=True,
            validate_responses=True, base_path='/storage',)

if __name__ == "__main__":
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()
    app.run(port=8090)

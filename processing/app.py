import connexion
from connexion import NoContent
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from apscheduler.schedulers.background import BackgroundScheduler
import datetime
import yaml
import logging
import logging.config
import mysql.connector
import pymysql
from os import path
import requests
import operator
import json
from flask_cors import CORS, cross_origin

# load config
with open('app_conf.yaml', 'r') as f:
    app_config = yaml.safe_load(f.read())

# configure logging
with open('log_conf.yaml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

filename = app_config["datastore"]['filename']


def populate_stats():
    """ Periodically update stats """
    # create datetime iso format zero hour offset
    current_datetime = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

    get_facts_url = "{}/facts/category".format(
        app_config["eventstore"]["url"])
    get_subscribers_url = "{}/facts/subscribe".format(
        app_config["eventstore"]["url"])

    # log processing start
    logger.info("Start Periodic Processing")

    # get current stats, else use default
    if not path.exists(filename):
        with open(filename, "w") as f:
            f.write(json.dumps({
                "num_users": 0,
                "num_facts": 0,
                "most_popular_tag": "",
                "avg_jokes_added_weekly": 0,
                "num_subscribed_users": 0,
                "last_datetime": current_datetime
            }, indent=4))
            f.close()

    # get current stats
    with open(filename, 'r') as f:
        currentstats = json.loads(f.read())
    # set current stats to variables
    curr_num_users = currentstats["num_users"]
    curr_num_facts = currentstats["num_facts"]
    curr_most_popular_tag = currentstats["most_popular_tag"]
    curr_avg_jokes_added_weekly = currentstats["avg_jokes_added_weekly"]
    curr_num_subscribed_users = currentstats["num_subscribed_users"]
    last_datetime = currentstats["last_datetime"]

    timestamp = current_datetime
    if last_datetime:
        timestamp = last_datetime

    ### call and log events ###
    # get first event
    get_facts_res = requests.get(
        get_facts_url, {"timestamp": timestamp})

    fact_status_code = get_facts_res.status_code

    # log first event
    if fact_status_code != 200:
        logger.error("request to {} with timestamp of {} returned {}".format(
            get_facts_url, timestamp, fact_status_code))
    else:
        fact_events = get_facts_res.json()
        logger.info("request to {} with timestamp of {} returned {} events".format(
            get_facts_url, timestamp, len(fact_events)))

    # get second event
    get_subscriber_res = requests.get(
        get_subscribers_url, {"timestamp": timestamp})

    subscriber_status_code = get_subscriber_res.status_code

    # log second event
    if subscriber_status_code != 200:
        logger.error("request to {} with timestamp of {} returned {}".format(
            get_subscribers_url, timestamp, subscriber_status_code))
    else:
        user_events = get_subscriber_res.json()
        logger.info("request to {} with timestamp of {} returned {} events".format(
            get_subscribers_url, timestamp, len((user_events))
        ))

    ### calculate new statistics ###
    # calculate num_users
    new_num_users = len(user_events)

    # calculate num_facts
    new_num_facts = len(fact_events)

    # calculate most_popular_tag
    tags = {}
    new_most_popular_tag = curr_most_popular_tag
    for fact in fact_events:
        for tag in fact["tags"]:
            if tag not in tags:
                tags[tag] = 1
            else:
                tags[tag] = tags[tag] + 1
    if len(tags):
        new_most_popular_tag = max(tags.items(), key=operator.itemgetter(1))[0]

    # calculate avg_jokes_added_weekly
    iso_facts_added = {}
    new_avg_jokes_added_weekly = 0
    for fact in fact_events:
        iso_datetime = datetime.datetime.strptime(
            fact["date_added"], '%Y-%m-%d %H:%M:%S.%f').isocalendar()
        # make key and convert to string
        key = "-".join(map(str, iso_datetime))
        if key not in iso_facts_added:
            iso_facts_added[key] = 1
        else:
            iso_facts_added[key] = iso_facts_added[key] + 1
    # take average
    if (len(iso_facts_added)):
        new_avg_jokes_added_weekly = sum(
            iso_facts_added.values()) / len(iso_facts_added)

    # calculate new_num_subscribed_users
    new_num_subscribed_users = 0
    for user in user_events:
        if user["subscribed"]:
            new_num_subscribed_users = new_num_subscribed_users + 1

    with open(filename, "w") as f:
        f.write(json.dumps({
                "num_users": new_num_users,
                "num_facts": new_num_facts,
                "most_popular_tag": new_most_popular_tag,
                "avg_jokes_added_weekly": new_avg_jokes_added_weekly,
                "num_subscribed_users": new_num_subscribed_users,
                "last_datetime": current_datetime
                }, indent=4))
        f.close()
    
    # CODE SNIPPET FOR ADDING
    # with open(filename, "w") as f:
    #     f.write(json.dumps({
    #             "num_users": curr_num_users + new_num_users,
    #             "num_facts": curr_num_facts + new_num_facts,
    #             "most_popular_tag": new_most_popular_tag,
    #             "avg_jokes_added_weekly": curr_avg_jokes_added_weekly + new_avg_jokes_added_weekly,
    #             "num_subscribed_users": curr_num_subscribed_users + new_num_subscribed_users,
    #             "last_datetime": current_datetime
    #             }, indent=4))
    #     f.close()

    # log processing end
    logger.info("Finished Periodic Processing")


def init_scheduler():
    """ creates scheduler """
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats, 'interval',
                  seconds=app_config['scheduler']['period_sec'])
    sched.start()


def get_stats():
    """ Returns interesting facts stats """
    logger.info("Retrieving stats")

    # if filename doesn't exist
    if not path.exists(filename):
        return "Statistics do not exist", 404

    # get current stats
    with open(filename, 'r') as f:
        currentstats = json.loads(f.read())

    # return json
    stats_obj = {}
    stats_obj["num_users"] = currentstats["num_users"]
    stats_obj["num_facts"] = currentstats["num_facts"]
    stats_obj["most_popular_tag"] = currentstats["most_popular_tag"]
    stats_obj["avg_jokes_added_weekly"] = currentstats["avg_jokes_added_weekly"]
    stats_obj["num_subscribed_users"] = currentstats["num_subscribed_users"]

    logger.debug(stats_obj)
    logger.info("Returning stats")
    return stats_obj, 200


app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("openapi.yaml", strict_validation=True,
            validate_responses=True, base_path='/',)

if __name__ == "__main__":
    init_scheduler()
    app.run(port=8100)

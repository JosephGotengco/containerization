from sqlalchemy import Column, Integer, String, DateTime, Boolean
from base import Base
import datetime


class User(Base):
    """ User """

    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    user_id = Column(String(250), nullable=False)
    username = Column(String(250), nullable=False)
    timestamp = Column(String(100), nullable=False)
    date_created = Column(DateTime, nullable=False)
    subscribed = Column(Boolean, nullable=False)

    def __init__(self, user_id, username, subscribed, timestamp):
        """ Initializes a user """
        self.user_id = user_id
        self.username = username
        self.date_created = datetime.datetime.now()
        self.subscribed = subscribed
        self.timestamp = timestamp

    def to_dict(self):
        """ Dictionary Representation of a user """
        dict = {}
        dict['id'] = self.id
        dict['user_id'] = self.user_id
        dict['username'] = self.username
        dict['date_created'] = self.date_created
        dict['subscribed'] = self.subscribed
        dict['timestamp'] = self.timestamp

        return dict

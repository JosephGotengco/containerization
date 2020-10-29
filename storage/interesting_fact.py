from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime


class InterestingFact(Base):
    """ Interesting Fact """

    __tablename__ = "facts"

    id = Column(Integer, primary_key=True)
    fact_id = Column(String(250), nullable=False)
    user_id = Column(String(250), nullable=False)
    fact = Column(String(250), nullable=False)
    tags = Column(String(250), nullable=False)
    timestamp = Column(String(100), nullable=False)
    date_added = Column(DateTime, nullable=False)

    def __init__(self, fact_id, user_id, fact, tags, timestamp):
        """ Initializes a interesting fact """
        self.fact_id = fact_id
        self.user_id = user_id
        self.fact = fact
        self.timestamp = timestamp
        self.date_added = datetime.datetime.now()
        self.tags = ','.join(tags)

    def to_dict(self):
        """ Dictionary Representation of a interesting fact """
        dict = {}
        dict['id'] = self.id
        dict['fact_id'] = self.fact_id
        dict['user_id'] = self.user_id
        dict['fact'] = self.fact
        dict['tags'] = self.tags.split(',')
        dict['timestamp'] = self.timestamp
        dict['date_added'] = self.date_added

        return dict

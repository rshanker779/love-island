from sqlalchemy import create_engine
from sqlalchemy import Column, Integer
from sqlalchemy.orm import sessionmaker
from rshanker779_common.logger import get_logger

from data_models.model_utilities import create_database, Dbconnection
from data_models.reddit_model import Base, Submission, Author, Comment

logger = get_logger(__name__)


class LoveIslandSubmission(Submission):
    episode_number = Column(Integer, nullable=False)


db_name = "love_island"

# TODO- get this working
love_island_db = Dbconnection("localhost", 5432, db_name, "ro_python")

user = "rohan"
password = "test1"


eng = create_engine("postgresql://%s:%s@localhost/love_island" % (user, password))


def get_session_and_create_databse():
    Session = sessionmaker()
    Session.configure(bind=eng)
    Base.metadata.create_all(eng)
    create_database(user, password, db_name)
    return Session


# class Comment(Base):
#     pass

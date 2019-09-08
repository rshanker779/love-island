from rshanker779_common.logger import get_logger
from sqlalchemy import Column, Integer, String, ForeignKey, Float, join, Boolean
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import UniqueConstraint, CreateTable

from data_models.model_utilities import create_database
from data_models.reddit_model import Base, Submission, Comment, Author, Word

logger = get_logger(__name__)

catchphrases = {
    "talented",
    "fanny flutters",
    "message",
    "young lady",
    "salmon",
    "bev",
    "chaldish",
    "categorically",
    "50k",
    "560",
}


class Islander(Base):
    __tablename__ = "islanders"
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.id == other.id


class CommentMention(Base):
    __tablename__ = "comment_mentions"
    """Designed to hold the many to many relationship between islander and comments"""
    id = Column(Integer, primary_key=True)
    islander_id = Column(Integer, ForeignKey("islanders.id"))
    comment_id = Column(String, ForeignKey("comments.id"))
    __table_args__ = (
        UniqueConstraint("islander_id", "comment_id", name="_comment_islander_uc"),
    )

    def __hash__(self):
        return hash((self.islander_id, self.comment_id))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return (other.comment_id, other.islander_id) == (
            self.islander_id,
            self.comment_id,
        )


class LoveIslandSubmission(Submission):
    episode_number = Column(Integer, nullable=False)


class LoveIslandComment(Comment):
    sentiment = Column(Float)


for i in catchphrases:
    i = "contains_" + i.replace(" ", "_")
    setattr(LoveIslandComment, i, Column(Boolean))

db_name = "love_island"
user = "rohan"
password = "test1"
eng = create_engine("postgresql://%s:%s@localhost/love_island" % (user, password))


def get_session_and_create_databse():
    Session = sessionmaker()
    Session.configure(bind=eng)
    Base.metadata.create_all(eng)
    create_database(user, password, db_name)
    return Session


def get_islander(first_name: str, last_name: str) -> Islander:
    return Islander(first_name=first_name, last_name=last_name)


def get_comment_mention(comment_id: str, islander_id: int) -> CommentMention:
    return CommentMention(comment_id=comment_id, islander_id=islander_id)

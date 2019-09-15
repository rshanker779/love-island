from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base


"""
Some ORM classes for python objects defined in PRAW packages
"""

Base = declarative_base()


class Submission(Base):
    __tablename__ = "submissions"
    id = Column(String, primary_key=True)
    fullname = Column(String, nullable=False)
    title = Column(String, nullable=False)
    author_id = Column(String, ForeignKey("authors.id"), nullable=False)
    author_flair_text = Column(String)
    created_utc = Column(DateTime, nullable=False)
    distinguished = Column(String)
    permalink = Column(String, nullable=False)
    score = Column(Integer)
    self_text = Column(String, nullable=False)
    # If building an ORM need to link foreign key as here:
    # https://docs.sqlalchemy.org/en/13/orm/tutorial.html#building-a-relationship

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)


class Author(Base):
    __tablename__ = "authors"
    id = Column(String, primary_key=True)
    name = Column(String)

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.id == other.id


class Comment(Base):
    __tablename__ = "comments"
    id = Column(String, primary_key=True)
    submission_id = Column(String, ForeignKey("submissions.id"), nullable=False)
    author_id = Column(String, ForeignKey("authors.id"), nullable=False)
    author_flair_text = Column(String)
    body = Column(String, nullable=False)
    created_utc = Column(DateTime, nullable=False)
    controversiality = Column(Integer)
    depth = Column(Integer)
    downs = Column(Integer)
    gilded = Column(Integer)
    parent_id = Column(String)
    permalink = Column(String)
    score = Column(Integer)
    score_hidden = Column(Boolean)
    ups = Column(Integer)

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.id == other.id


class Word(Base):
    __tablename__ = "words"
    id = Column(Integer, primary_key=True)
    body = Column(String, nullable=False)
    is_stop = Column(Boolean, nullable=False)
    importance = Column(Float)

    def __hash__(self):
        return hash(self.body)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.body == other.body

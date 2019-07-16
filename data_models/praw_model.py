from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base


"""
Some ORM classes for python objects defined in PRAW packages
"""

Base = declarative_base()


class Submission(Base):
    __tablename__ = "submissions"
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    author_fullname = Column(String, ForeignKey("authors.fullname"))
    author_flair_text = Column(String)
    created_utc = Column(DateTime, nullable=False)
    distinguished = Column(String)
    permalink = Column(String, nullable=False)
    score = Column(Integer)
    self_text = Column(String, nullable=False)
    # If building an ORM need to link foreign key as here:
    # https://docs.sqlalchemy.org/en/13/orm/tutorial.html#building-a-relationship

    def __eq__(self, other):
        if not isinstance(other, Submission):
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)


class Author(Base):
    __tablename__ = "authors"
    fullname = Column(String, primary_key=True)
    name = Column(String)

    def __hash__(self):
        return hash(self.fullname)

    def __eq__(self, other):
        if not isinstance(other, Author):
            return False
        return self.fullname == other.fullname

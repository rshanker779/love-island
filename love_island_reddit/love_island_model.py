from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
import psycopg2
from rshanker779_common.logger import get_logger
from sqlalchemy.exc import ProgrammingError

logger = get_logger(__name__)


class Dbconnection:
    def __init__(self, host, port, db, username, driver="postgresql"):
        self.host = host if host != "localhost" else ""
        self.port = port
        self.db = db
        self.driver = driver
        self.conn_string = "{}://{}@{}:{}/{}".format(driver, username, host, port, db)


db_name = "love_island"
# TODO- get this working
love_island_db = Dbconnection("localhost", 5432, db_name, "ro_python")

Base = declarative_base()
user = "rohan"
password = "dunno"
eng = create_engine("postgresql://%s:%s@localhost/love_island" % (user, password))
Session = sessionmaker()
Session.configure(bind=eng)


def create_database(
    username: str, password: str, database: str, connection_database="postgres"
):
    try:
        engine = create_engine(
            "postgresql://{}:{}@localhost/{}".format(
                username, password, connection_database
            )
        )
        conn = engine.connect()
        # Sqlalchemy starts everything in transaction, we cannot create db in transaction so must first close transaction
        conn.execute("commit;")
        conn.execute("create database {};".format(database))
        conn.close()
    except ProgrammingError as e:
        if isinstance(e.orig, psycopg2.errors.DuplicateDatabase):
            logger.info("Database already exists")
        else:
            raise


class Submission(Base):
    __tablename__ = "submissions"
    id = Column(Integer, primary_key=True)
    title = Column(String)


create_database(user, password, db_name)
Base.metadata.create_all(eng)

# class Comment(Base):
#     pass

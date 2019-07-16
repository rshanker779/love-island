import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.exc import ProgrammingError
from rshanker779_common.logger import get_logger

logger = get_logger(__name__)


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


class Dbconnection:
    def __init__(self, host, port, db, username, driver="postgresql"):
        self.host = host if host != "localhost" else ""
        self.port = port
        self.db = db
        self.driver = driver
        self.conn_string = "{}://{}@{}:{}/{}".format(driver, username, host, port, db)

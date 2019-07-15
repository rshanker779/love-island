"""
https://www.reddit.com/dev/api/
"""
import json
import os
import praw
from rshanker779_common.logger import get_logger

logger = get_logger(__name__)


class BotParams:
    user_agent = "jgodfrey:python:requests:v1.0.0"
    try:
        with open(os.path.join(os.path.dirname(__file__), "config.json"), "r") as f:
            config_json = json.load(f)
        client_id = config_json["client_id"]
        client_secret = config_json["client_secret"]
        user_name = config_json["username"]
        password = config_json["password"]
    except FileNotFoundError:
        logger.exception("File not found, make sure config.json exists")
    except KeyError:
        logger.exception(
            "Required key not found, make sure config.json has same fields as example"
        )


def get_authenticated_reddit_connection():
    reddit = praw.Reddit(
        client_id=BotParams.client_id,
        client_secret=BotParams.client_secret,
        user_agent=BotParams.user_agent,
        username=BotParams.user_name,
        password=BotParams.password,
    )
    for _ in reddit.subreddit("python").hot(limit=1):
        # This line may seem pointless, but this requests will throw an
        # error if permissioning hasn't worked.
        pass
    return reddit


if __name__ == "__main__":
    get_authenticated_reddit_connection()

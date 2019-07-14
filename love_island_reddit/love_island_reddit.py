from reddit.reddit_api import get_authenticated_reddit_connection
from rshanker779_common.logger import get_logger
import re

logger = get_logger(__name__)
"""
Initially will just grab all comments from the episode and post episode threads
"""


# searchstr = "'rule' timestamp:{}..{}".format(start,end)


class Constants:
    love_island_subreddit = "LoveIslandTV"
    episode_title_match = re.compile("Episode \d")


def main():
    global reddit
    reddit = get_authenticated_reddit_connection()
    for sumbission in reddit.subreddit(Constants.love_island_subreddit).new(limit=100):
        if Constants.episode_title_match.match(sumbission.title) is not None:
            logger.info(sumbission.title)


if __name__ == "__main__":
    main()

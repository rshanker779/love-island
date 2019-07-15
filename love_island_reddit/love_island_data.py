from reddit.reddit_api import get_authenticated_reddit_connection
from rshanker779_common.logger import get_logger
import logging
import re
from datetime import datetime
import love_island_reddit.love_island_model as li_model

logger = get_logger(__name__, logging.DEBUG)
"""
Initially will just grab all comments from the episode and post episode threads
"""


class Constants:
    love_island_subreddit = "LoveIslandTV"
    episode_title_match = re.compile("Episode (\d+)")


def main():
    searchstr = "Episode"
    reddit = get_authenticated_reddit_connection()
    found_episodes = set()
    found_dates = set()
    session = li_model.Session()
    for submission in reddit.subreddit(Constants.love_island_subreddit).search(
        searchstr, sort="relevance", syntax="lucene", limit=None
    ):
        episode_match = Constants.episode_title_match.match(submission.title)
        if episode_match is not None:
            episode_num = episode_match.group(1)
            model_sumbission = li_model.Submission(title=submission.title)
            session.add(model_sumbission)
            found_episodes.add(episode_num)
            found_dates.add(submission.created_utc)
    session.commit()
    if found_episodes - set(
        str(i) for i in range(max(int(i) for i in found_episodes) + 1)
    ):
        return


if __name__ == "__main__":
    main()

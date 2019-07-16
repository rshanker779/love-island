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
    Session = li_model.get_session_and_create_databse()
    searchstr = "Episode"
    reddit = get_authenticated_reddit_connection()
    authors = set()
    submissions = set()
    relevant_submissions = reddit.subreddit(Constants.love_island_subreddit).search(
        searchstr, sort="relevance", syntax="lucene", limit=None
    )
    for submission in relevant_submissions:
        episode_match = Constants.episode_title_match.match(submission.title)
        if episode_match is not None:
            episode_num = episode_match.group(1)
            model_sumbission = li_model.LoveIslandSumbission(
                id=submission.id,
                title=submission.title,
                author_fullname=submission.author.fullname,
                author_flair_text=submission.author_flair_text,
                created_utc=datetime.fromtimestamp(submission.created_utc),
                distinguished=submission.distinguished,
                permalink=submission.permalink,
                score=submission.score,
                self_text=submission.selftext,
                episode_number=episode_num,
            )
            author = li_model.Author(
                fullname=submission.author.fullname, name=submission.author.name
            )
            authors.add(author)
            submissions.add(model_sumbission)
    session = Session()

    session.add_all(authors)
    session.commit()
    session = Session()
    session.add_all(submissions)
    # session.add(author)
    session.commit()


if __name__ == "__main__":
    main()

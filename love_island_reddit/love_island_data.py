from reddit.reddit_api import get_authenticated_reddit_connection
from rshanker779_common.logger import get_logger
import logging
import re
from datetime import datetime
import love_island_reddit.love_island_model as li_model
from praw.models import Comment, Redditor, Submission, MoreComments
from prawcore.exceptions import NotFound
import data_models.praw_to_reddit_mapper as mapper

logger = get_logger(__name__, logging.DEBUG)

"""
Initially will just grab all comments from the episode and post episode threads
"""


class Constants:
    love_island_subreddit = "LoveIslandTV"
    episode_title_match = re.compile("Episode (\d+)")


class InsertCollection:
    """
    Class to collect all the classes that will be written
    to the db. Allows us to control insert order
    """

    def __init__(self):
        self.authors = set()
        self.comments = set()
        self.submissions = set()

    def add_author(self, author: li_model.Author):
        self.authors.add(author)

    def add_comments(self, comment: li_model.Comment):
        self.comments.add(comment)

    def add_submission(self, submission: li_model.Submission):
        self.submissions.add(submission)


def main():
    Session = li_model.get_session_and_create_databse()
    session = Session()
    existing_submissions = {i[0] for i in session.query(li_model.Submission.id).all()}
    session.commit()
    session = Session()
    existing_authors = {i[0] for i in session.query(li_model.Author.id).all()}
    session.commit()
    searchstr = "Episode"
    reddit = get_authenticated_reddit_connection()
    relevant_submissions = reddit.subreddit(Constants.love_island_subreddit).search(
        searchstr, sort="relevance", syntax="lucene", limit=None
    )
    for submission in relevant_submissions:
        inserts = InsertCollection()
        if submission.id in existing_submissions:
            continue
        episode_match = Constants.episode_title_match.match(submission.title)
        if episode_match is not None:
            episode_num = int(episode_match.group(1))
            model_submission = get_love_island_submission(submission, episode_num)
            get_all_post_comments(submission, inserts)
            logger.info(inserts.comments)
            logger.info(len(inserts.comments))
            logger.info(len(inserts.authors))
            author = mapper.get_author(submission.author)
            inserts.add_author(author)
            inserts.add_submission(model_submission)

        session = Session()

        session.add_all({i for i in inserts.authors if i.id not in existing_authors})
        session.commit()
        existing_authors |= {i.id for i in inserts.authors}
        session = Session()
        session.add_all(inserts.submissions)
        session.commit()
        session = Session()
        session.add_all(inserts.comments)
        session.commit()


def get_all_post_comments(submission: Submission, insert: InsertCollection):
    submission.comments.replace_more(limit=None)
    for comment in submission.comments.list():
        if comment.body != "[deleted]" and comment.author is not None:
            logger.info(comment.body)
            logger.info(comment.author)
            try:
                insert.add_author(mapper.get_author(comment.author))
                model_comment = mapper.get_comment(comment)
                insert.add_comments(model_comment)
            except Exception:
                # This occurs if author has deleted their account for instance
                logger.exception("Error getting comment %s", comment)
        else:
            logger.info(comment.body)
            logger.info(comment.id)


def get_love_island_submission(
    submission: Submission, episode_num: int
) -> li_model.Submission:
    return li_model.LoveIslandSubmission(
        id=submission.id,
        fullname=submission.fullname,
        title=submission.title,
        author_id=submission.author.id,
        author_flair_text=submission.author_flair_text,
        created_utc=datetime.fromtimestamp(submission.created_utc),
        distinguished=submission.distinguished,
        permalink=submission.permalink,
        score=submission.score,
        self_text=submission.selftext,
        episode_number=episode_num,
    )


if __name__ == "__main__":
    main()

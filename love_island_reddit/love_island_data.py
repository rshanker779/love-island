import logging
import re

import pandas as pd
import requests as r
from praw.models import Submission
from rshanker779_common.logger import get_logger
import data_models.praw_to_reddit_mapper as mapper
import love_island_reddit.love_island_model as li_model
from reddit.reddit_api import get_authenticated_reddit_connection
import spacy
from datetime import datetime, timedelta
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
import tqdm

nltk.download("vader_lexicon")

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
    existing_authors = {i[0] for i in session.query(li_model.Author.id).all()}
    session.commit()
    searchstr = "Episode"
    reddit = get_authenticated_reddit_connection()
    existing_islanders = session.query(li_model.Islander).all()
    new_islanders = get_new_islanders(existing_islanders)
    session.add_all(new_islanders)
    session.commit()
    relevant_submissions = reddit.subreddit(Constants.love_island_subreddit).search(
        searchstr, sort="relevance", syntax="lucene", limit=None
    )
    get_new_comments(
        existing_authors, existing_submissions, relevant_submissions, session
    )
    get_comment_mentions_and_words(session)
    compute_vader_sentiment_analysis_scores(session)
    # get_words(Session)


def get_new_comments(
    existing_authors, existing_submissions, relevant_submissions, session
):
    for submission in relevant_submissions:
        if datetime.fromtimestamp(submission.created_utc) > datetime.now() - timedelta(
            hours=24
        ):
            logger.info(
                "Not writing any data for submission %s as less that 24 hours old",
                submission.id,
            )
            continue
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
        # Separate sessions are to ensure db inserts done in order

        session.add_all({i for i in inserts.authors if i.id not in existing_authors})
        session.commit()
        existing_authors |= {i.id for i in inserts.authors}
        session.add_all(inserts.submissions)
        session.commit()
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
    return mapper.get_submission(
        submission, li_model.LoveIslandSubmission, episode_number=episode_num
    )


def get_islander_information(series=5):
    url = "http://en.wikipedia.org/wiki/Love_Island_(series_{})"
    response = r.get(url.format(series))
    response.raise_for_status()
    dfs = pd.read_html(response.text)
    for df in dfs:
        if "Islander" in df.columns:
            islander_df = df
            islander_df[["first_name", "last_name"]] = islander_df[
                "Islander"
            ].str.split(" ", expand=True, n=2)
            # Molly-Mae causes tokenization issues, so we replace with Molly
            islander_df.loc[
                islander_df["first_name"] == "Molly-Mae", "first_name"
            ] = "Molly"
            return islander_df
    return pd.DataFrame()


def get_new_islanders(existing_islanders):
    # Make the reasonable assumption no two islanders with matching names
    existing_names = {(i.first_name, i.last_name) for i in existing_islanders}
    new_islander = set()
    islander_df = get_islander_information()
    islander_df["islander_model"] = islander_df.apply(
        lambda x: li_model.get_islander(x["first_name"], x["last_name"]), axis=1
    )
    for islander in islander_df["islander_model"]:
        if (islander.first_name, islander.last_name) not in existing_names:
            new_islander.add(islander)
    return new_islander


def get_comment_mentions_and_words(session):
    """
    We go through all our comments, tokenize with spacy,
    check if they mention an islander and put appropriate mapping in
    comment_mentions
    """
    nlp = spacy.load("en_core_web_sm")
    comments = session.query(li_model.LoveIslandComment).all()
    islanders = session.query(li_model.Islander).all()
    comment_mentions = session.query(li_model.CommentMention).all()
    existing_words = {i.body.lower() for i in session.query(li_model.Word).all()}
    # #we assume if a comment is in mentions all mentions have been processed
    existing_mentions = {i.comment_id for i in comment_mentions}
    islander_name_map = {i.first_name.lower(): i.id for i in islanders}
    commention_mention_set = {(i.islander_id, i.comment_id) for i in comment_mentions}
    mentions = set()
    comments_to_process = comments#{i for i in comments if i.id not in existing_mentions}
    all_words = set()
    for comment in tqdm.tqdm(comments_to_process):
        doc = nlp(comment.body)
        comment_words = {li_model.Word(body=i.text.lower(), is_stop=i.is_stop) for i in doc if i.text.lower() not in existing_words}
        all_words |=comment_words
        islanders_mentioned = {i.text.lower() for i in doc} & islander_name_map.keys()
        for islander in islanders_mentioned:
            mention = li_model.get_comment_mention(
                comment.id, islander_name_map[islander]
            )
            if (mention.islander_id, mention.comment_id) not in commention_mention_set:
                logger.info("Comment %s mentions %s", comment.body, islander)

                mentions.add(mention)
    session.add_all(all_words)
    session.add_all(mentions)
    session.commit()
    for phrase in li_model.catchphrases:
        phrase_components = set(phrase.split(" "))
        phrase = phrase.replace(" ", "_")
        col_name = "contains_" + phrase
        comments_to_process = {i for i in comments if getattr(i, col_name) is None}
        for comment in comments_to_process:
            doc = nlp(comment.body)
            contains_phrase = bool({i.text for i in doc} & phrase_components)
            if contains_phrase:
                logger.info("Comment %s mentions %s", comment.body, phrase)
            setattr(comment, col_name, contains_phrase)
            session.add(comment)
    session.commit()


def compute_vader_sentiment_analysis_scores(session):
    comments = (
        session.query(li_model.LoveIslandComment)
        .filter(li_model.LoveIslandComment.sentiment.is_(None))
        .all()
    )
    analyzer = SentimentIntensityAnalyzer()
    for comment in comments:
        comment.sentiment = analyzer.polarity_scores(comment.body)["compound"]
    session.commit()



if __name__ == "__main__":
    main()

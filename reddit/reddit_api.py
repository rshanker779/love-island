"""
https://www.reddit.com/dev/api/
"""
import json
import requests as r
import os
import praw


class BotParams:
    user_agent = "jgodfrey:python:requests:v1.0.0"
    with open(os.path.join(os.path.dirname(__file__), "config.json"), "r") as f:
        config_json = json.load(f)
    client_id = config_json["client_id"]
    client_secret = config_json["client_secret"]
    user_name = config_json["username"]
    password = config_json["password"]


class BaseUrl:
    url = "http://reddit.com/api/v1/"


class MeEndpoints(BaseUrl):
    me_endpoint = BaseUrl.url + "me/"


def main():
    reddit = praw.Reddit(
        client_id=BotParams.client_id,
        client_secret=BotParams.client_secret,
        user_agent=BotParams.user_agent,
        username=BotParams.user_name,
        password=BotParams.password,
    )
    for post in reddit.subreddit("LoveIslandTV").hot(limit=10):
        print(post)
    return


if __name__ == "__main__":
    main()

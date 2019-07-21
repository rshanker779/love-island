"""
https://pushshift.io/api-parameters/
https://github.com/dmarx/psaw
"""
import psaw
from psaw import PushshiftAPI
from datetime import datetime


def main():
    api = PushshiftAPI()

    start = datetime(2019, 5, 1, 0, 0, 0)
    submissions = api.search_submissions(
        after=int(start.timestamp()), subreddit="LoveIslandTV", limit=1
    )
    submissions = list(submissions)


if __name__ == "__main__":
    main()

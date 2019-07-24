import love_island_reddit.love_island_model as li_model
import os


def main():
    with open(
        os.path.join(os.path.dirname(__file__), "single_user_comments.sql"), "r"
    ) as f:
        single_mentions_query = f.read()
    Session = li_model.get_session_and_create_databse()
    session = Session()
    # TODO


if __name__ == "__main__":
    main()

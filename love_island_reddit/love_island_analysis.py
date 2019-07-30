import love_island_reddit.love_island_model as li_model
import os
from sqlalchemy import text
from collections import Counter
import pandas as pd

aggregated_data_file_name = "comments.csv"
data_path = os.path.dirname(__file__)
aggregated_data_file_path = os.path.join(data_path, aggregated_data_file_name)
regenerate_data = False


def main():
    if not regenerate_data and os.path.isfile(aggregated_data_file_path):
        df = pd.read_csv(aggregated_data_file_path)
    else:
        df = generate_data()
    # TODO
    # pi chart of comment count by islander
    # 5 min sentiment for each episode and islander (interactive)
    # popularity ranking at each time
    # biggest swings per episode
    # most hated islander
    # most loved islander
    # Keyword analysis
    df.plot()
    return


def generate_data():
    with open(
        os.path.join(os.path.dirname(__file__), "single_user_comments.sql"), "r"
    ) as f:
        single_mentions_query = f.read()
    Session = li_model.get_session_and_create_databse()
    session = Session()
    results = (
        session.query(
            li_model.LoveIslandComment, li_model.Islander, li_model.Submission
        )
        .from_statement(text(single_mentions_query))
        .all()
    )
    # Unpack the dicts to make a tabular df for analysis
    rows = [
        {
            **res.Islander.__dict__,
            **res.LoveIslandComment.__dict__,
            **res.Submission.__dict__,
        }
        for res in results
    ]
    df = pd.DataFrame(rows)
    df = df[[i for i in df.columns if i != "_sa_instance_state"]]
    df.to_csv(aggregated_data_file_path)
    return df


if __name__ == "__main__":
    main()

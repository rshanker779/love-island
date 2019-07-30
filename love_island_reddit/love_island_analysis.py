import love_island_reddit.love_island_model as li_model
import os
from sqlalchemy import text
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
aggregated_data_file_name = "comments.csv"
data_path = os.path.dirname(__file__)
aggregated_data_file_path = os.path.join(data_path, aggregated_data_file_name)
regenerate_data = False


def main():
    if not regenerate_data and os.path.isfile(aggregated_data_file_path):
        df = pd.read_csv(aggregated_data_file_path, index_col=0)
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
    count_by_name_df = df.groupby('first_name').count().sort_values('id')
    fig = go.Figure(go.Pie(labels=count_by_name_df.index, values=count_by_name_df['id']))
    fig.show()
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

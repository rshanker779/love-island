#Note this will be run in jupyer notebook. So to make imports easier,
#imports of my packages will be in specific functions
import os
from sqlalchemy import text
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
# import plotly.plotly as py





def main():
    import love_island_reddit.love_island_model as li_model
    aggregated_data_file_name = "comments.csv"
    data_path = os.path.dirname(__file__)
    aggregated_data_file_path = os.path.join(data_path, aggregated_data_file_name)
    regenerate_data = False
    if not regenerate_data and os.path.isfile(aggregated_data_file_path):
        df = pd.read_csv(aggregated_data_file_path, index_col=0)
    else:
        df = generate_data(aggregated_data_file_path)
    df['created_utc'] = pd.to_datetime(df['created_utc'])
    time_df = df.set_index('created_utc')
    grouper = time_df.groupby([pd.Grouper(freq='30min'), 'first_name'] )
    sentiment_by_time = grouper['sentiment'].mean().unstack()
    sentiment_by_time = sentiment_by_time.sort_index()
    sentiment_by_time = sentiment_by_time.fillna(method='ffill', axis=0)
    sentiment_by_time = sentiment_by_time.stack()
    sentiment_by_time = sentiment_by_time.rename('sentiment')
    sentiment_by_time = sentiment_by_time.reset_index()
    # sentiment_by_time['post_time'] = sentiment_by_time.index
    # show_times = df['post_time'].
    posted_during_show = (sentiment_by_time['created_utc'].dt.time > pd.to_datetime('21:00:00').time()) &(sentiment_by_time['created_utc'].dt.time < pd.to_datetime('22:00:00').time())
    sentiment_by_time = sentiment_by_time.loc[posted_during_show]
    # TODO
    # 5 min sentiment for each episode and islander (interactive)
    # popularity ranking at each time
    # biggest swings per episode
    # most hated islander
    # most loved islander
    # Keyword analysisfe
    fig = get_count_by_name_chart(df)
    fig = get_time_sentiment_chart(sentiment_by_time)
    fig.show()
    for i in li_model.catchphrases:
        col_name = 'contains_'+i.replace(' ','_')


    catchprase_col_names = {'contains_'+i.replace(' ','_') for i in li_model.catchphrases}

    return

def get_count_by_name_chart(df):
    count_by_name_df = df.groupby("first_name").count().sort_values("id")
    fig = go.Figure(
        go.Pie(labels=count_by_name_df.index, values=count_by_name_df["id"])
    )
    return fig

def get_time_sentiment_chart(df):
    df['created_utc'] = df.index
    df = df.sort_index()
    fig = px.line(df, x='created_utc',y='sentiment', color='first_name')

    return fig


def generate_data(data_path):
    import love_island_reddit.love_island_model as li_model
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
    df.to_csv(data_path)
    return df


#__file__ check prevents this running on Ipython
if __name__ == "__main__"  and '__file__' in globals():
    main()

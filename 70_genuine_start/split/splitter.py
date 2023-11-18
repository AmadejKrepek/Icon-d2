from split.split_df import split_dataframe_by_hour


def split_data(df):
    dfs = split_dataframe_by_hour(df)
    return dfs

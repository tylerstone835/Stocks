from datetime import datetime

import pandas as pd


def natural_join(
        *dfs: pd.DataFrame,
        how: str = 'inner',
) -> pd.DataFrame | None:
    """
    Merges two pd.DataFrame objects based on overlapping column labels.
        :param *dfs: One or many dataframe objects to naturally join.
        :param how: Join type to be performed (e.g., inner, left, right, outer, cross)
        :return: Joined pd.DataFrame object.
    """
    master_df = pd.DataFrame()

    for df in dfs:
        if master_df.empty:
            master_df = df
            continue

        columns_list = list(master_df.columns) + list(df.columns)

        dupe_labels_df = (
            pd.Series(columns_list)
            .value_counts()
            .reset_index()
        )

        dupe_labels_list = dupe_labels_df.loc[dupe_labels_df['count'] > 1]['index'].to_list()

        if dupe_labels_list:
            master_df = master_df.merge(df, how=how, on=dupe_labels_list)

    return master_df


def build_df_from_map(
    map: dict,
    ticker: str,
) -> pd.DataFrame:
    """
    Creates pd.DataFrame for designated symbol based on the table_map structure.

    :param map: dict object containing the callables and params necessary to make table in map.
    :ticker: Ticker symbol for a publicly traded stock.
    """

    # Construct master dataframe with callables with params in table_map
    df_list = []
    for column in map:
        if map[column]['callable'] is None or map[column]['params'] is None:
            continue

        callable = map[column]['callable']
        params = map[column]['params']

        df_list.append(callable(ticker=ticker, **params ))

    master_df = natural_join(*df_list, how='inner')

    # Modify constructed master dataframe with callables stored without params.
    for column in map:
        if map[column]['callable'] is None or map[column]['params'] is not None:
            continue

        callable = map[column]['callable']
        callable(master_df)

    return master_df


def timestamp_to_date(df: pd.DataFrame) -> None:
    """
    """
    if 'timestamp' not in df.columns:
        return

    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms').dt.strftime('%Y-%m-%d')
    df.rename(columns={'timestamp': 'date'}, inplace=True)

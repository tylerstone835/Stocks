from datetime import datetime

import pandas as pd

from table_maps import daily_table_map


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
    table_map: dict,
    ticker: str,
) -> pd.DataFrame:
    """
    Creates pd.DataFrame for designated symbol based on the table_map structure.

    :param table_map: dict object containing the callables and params necessary to make table in map.
    :ticker: Ticker symbol for a publicly traded stock.
    """

    df_list = []
    for column in table_map:
        if table_map[column]['callable'] is None or table_map[column]['params'] is None:
            continue

        callable = table_map[column]['callable']
        params = table_map[column]['params']

        df_list.append(callable(ticker=ticker, **params ))

    return natural_join(*df_list, how='inner')

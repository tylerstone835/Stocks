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


def timestamp_to_date(
    df: pd.DataFrame,
) -> None:
    """
    Converts the unix[ms] timestamp column to a readable date column.

    :param df: DataFrame containing a timestamp column.
    """

    if 'timestamp' not in df.columns:
        return

    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms').dt.strftime('%Y-%m-%d')
    df.rename(columns={'timestamp': 'date'}, inplace=True)


def calculate_variance(
    df: pd.DataFrame,
    spine: str = 'ema_20',
) -> None:
    """
    Finds the max variance between the high/low and the selected spine (usually 20-period).
    Raises a ValueError if data needed for calculation isn't found (price action and at least on EMA)

    :param df: Target DataFrame.
    :param spine: Series label of the ema you wish to find a variance of. (Typically 20-period)
    """

    if spine not in df.columns or 'high' not in df.columns or 'low' not in df.columns:
        raise ValueError('high, low or designated spine not found in submitted pd.DataFrame.')

    df['high_difference'] = abs(df['high'] - df[spine])
    df['low_difference'] = abs(df['low'] - df[spine])

    df['max_difference'] = df[['high_difference', 'low_difference']].max(axis=1)
    df['variance'] = round(df['max_difference'] / df[spine], 4)

    df.drop(columns=['high_difference', 'low_difference', 'max_difference'], inplace=True)

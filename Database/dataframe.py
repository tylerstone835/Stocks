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

    df['high_difference'] = abs(df['high'] - df[spine])
    df['low_difference'] = abs(df['low'] - df[spine])

    df['max_difference'] = df[['high_difference', 'low_difference']].max(axis=1)
    df['variance'] = round(df['max_difference'] / df[spine], 4)

    df.drop(columns=['high_difference', 'low_difference', 'max_difference'], inplace=True)


def percentile(
        series: pd.Series,
) -> float:
    """
    Custom pd.Agg function to apply as a rolling window function.
    This will return the value that defines the 95th percentile limit
    over a specified rolling period.
        :param series: pd.Series object passed from pd.series.agg()
        :return: Scalar value representing the 95th percentile in series.
    """
    sorted_series_values = sorted(series.to_list())
    percentile_index = int(len(sorted_series_values) * .95) - 1

    return sorted_series_values[percentile_index]


def calculate_keltner_channels(
        df: pd.DataFrame,
        spine: str = 'ema_20',
        window: int = 125,
) -> None:
    """
    Adds Keltner Channels based on the specified EMA spine. Rolling channels are based
    on a designated window, usually 125 periods for daily and 26 periods for weekly,
    or approximately 6 months. Will raise a ValueError if price action data is not found
    in object's dataframe.

    :param df: Target pd.DataFrame
    :param spine: EMA window to base channels on.
    :param window: Number of rolling periods used in percentile window function.
    """
    if 'high' not in df.columns or 'low' not in df.columns or spine not in df.columns:
        raise ValueError('Base data needed for calculation not found. Please run get_price_action and/or get_ema '
                         'before running get_keltner_channels')

    if len(df) < window:
        df[['deviation', 'upper_channel', 'lower_channel']] = None
        return

    calculate_variance(df, spine)
    df['deviation'] = df['variance'].rolling(window).agg(percentile)

    df['upper_channel'] = round(df[spine] * (df['deviation'] + 1), 2)
    df['lower_channel'] = round(df[spine] * (1 - df['deviation']), 2)
    df.drop(columns=['variance'], inplace=True)


def calculate_impulse(
    df: pd.DataFrame,
    spine: str = 'ema_10',
) -> None:
    """
    Adds an impulse indicator based on a combination of the macd_histogram
    column and a designated spine. Spine is usually the intermediate period EMA,
    or the 10 period EMA. Will raise a ValueError if macd data or ema data is
    not found in object's dataframe.
        :param df: Target pd.DataFrame
        :param spine: Designated spine for comparison against MACD Histogram.
    """
    if 'macd_histogram' not in df.columns or spine not in df.columns:
        raise ValueError('Base data needed for calculation not found. Please run get_macd and/or get_ema '
                         'before running get_impulse.')

    if len(df) < 2:
        df['impulse'] = 'Red'
        return

    df['ema_impulse'] = df[spine].rolling(2).max()
    df['macd_impulse'] = df['macd_histogram'].rolling(2).max()

    df['macd_rising'] = df['macd_impulse'] == df['macd_histogram']
    df['ema_rising'] = df['ema_impulse'] == df[spine]

    df['impulse'] = df[['macd_rising', 'ema_rising']].sum(axis=1)
    df['impulse'] = df['impulse'].map({0: 'Red', 1: 'Blue', 2: 'Green'})

    df.drop(columns=['ema_impulse', 'macd_impulse', 'macd_rising', 'ema_rising'], inplace=True)


def calculate_atr(
    df: pd.DataFrame,
    window: int = 14,
) -> None:
    """
    Adds ATR indicator data to the batch. If price action data (high, low, close) is
    not found in df, it will raise a ValueError. Uses SMA, not WMA.
        :param df: Target DataFrame.
        :param window: rolling period for ATR average.
    """
    if 'close' not in df.columns or 'high' not in df.columns or 'low' not in df.columns:
        raise ValueError('Base data needed for calculation not found. Please run get_price_action '
                         'before running get_atr.')

    if len(df) < window:
        df['atr'] = None
        return

    df['yest_close'] = df['close'].shift(1)
    df['high_low_diff'] = df['high'] - df['low']
    df['high_close_diff'] = abs(df['yest_close'] - df['high'])
    df['low_close_diff'] = abs(df['yest_close'] - df['low'])
    df['pre_atr'] = df[['high_low_diff', 'high_close_diff', 'low_close_diff']].max(axis=1)
    df['atr'] = df['pre_atr'].rolling(window).mean().round(3)

    df.drop(columns=['yest_close', 'high_low_diff', 'high_close_diff', 'low_close_diff', 'pre_atr'], inplace=True)

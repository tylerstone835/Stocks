from datetime import date, timedelta

import holidays
import pandas as pd


START_DATE = date.today() - timedelta(days=365*5)
END_DATE = date.today()


def calculate_date_table(
    start: date = START_DATE,
    end: date = END_DATE
) -> pd.DataFrame:
    """
    Calculates a date table for SQL database with overridable start, end dates.

    :param start: Start date for the date table.
    :param end: End date for the date table.
    :return: pd.DataFrame containing calculated date table.
    """

    us_holidays = holidays.country_holidays('US')
    nyse_holidays = holidays.financial_holidays('NYSE')

    df = pd.DataFrame({'date': pd.date_range(start=start, end=end)})
    df['description'] = df['date'].apply(lambda x: x.strftime('%B %#d, %Y'))
    df['day'] = df['date'].apply(lambda x: x.day_name())
    df['day_of_week'] = df['date'].apply(lambda x: x.day_of_week)
    df['day_of_month'] = df['date'].apply(lambda x: x.day)
    df['day_of_year'] = df['date'].apply(lambda x: x.day_of_year)

    df['week_number'] = df['date'].apply(lambda x: x.week)

    df['month'] = df['date'].apply(lambda x: x.month_name())
    df['month_number'] = df['date'].apply(lambda x: x.month)
    df['is_month_start'] = df['date'].apply(lambda x: x.is_month_start)
    df['is_month_end'] = df['date'].apply(lambda x: x.is_month_end)

    df['year'] = df['date'].apply(lambda x: x.year)
    df['is_year_start'] = df['date'].apply(lambda x: x.is_year_start)
    df['is_year_end'] = df['date'].apply(lambda x: x.is_year_end)
    df['is_leap_year'] = df['date'].apply(lambda x: x.is_leap_year)

    df['is_holiday'] = df['date'].apply(lambda x: x in us_holidays)
    df['holiday'] = df['date'].apply(lambda x: us_holidays.get(x, None))

    df['is_market_holiday'] = df['date'].apply(lambda x: x in nyse_holidays)
    df['market_holiday'] = df['date'].apply(lambda x: nyse_holidays.get(x, None))

    df['date'] = df['date'].astype('string')

    return df


def natural_join(
    *dfs: pd.DataFrame,
    how: str = 'left',
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

        dupe_labels_list = list(set(master_df.columns) & set(df.columns))

        if dupe_labels_list:
            master_df = master_df.merge(df, how=how, on=dupe_labels_list)

    return master_df


def timestamp_to_date(
    df: pd.DataFrame,
    timespan: str = 'day',
) -> None:
    """
    Converts the unix[ms] timestamp column to a readable date column.
    Weekly needs to be offset by one day to match market standards.

    :param df: DataFrame containing a timestamp column.
    :param timespan: Identifies if timestamp contains daily values, or weekly.
    """

    if 'timestamp' not in df.columns:
        raise ValueError('timestamp not found in DataFrame object')

    if timespan == 'week':
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df['timestamp'] = df['timestamp'] + timedelta(days=1)
        df['timestamp'] = df['timestamp'].dt.strftime('%Y-%m-%d')
        df.rename(columns={'timestamp': 'date'}, inplace=True)
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
        raise ValueError('Necessary data for calculation not found...')

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

    calculate_variance(df, spine)

    df['deviation'] = (
        df[['symbol', 'variance']]
        .groupby('symbol')
        .rolling(window)
        .agg(percentile)
        .reset_index(drop=True)
    )

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
        print('macd and/or ema spine was not found...')
        df['impulse'] = 'Red'
        return

    df['ema_impulse'] = df[['symbol', spine]].groupby('symbol').rolling(2).min().reset_index(drop=True)
    df['macd_impulse'] = df[['symbol', 'macd_histogram']].groupby('symbol').rolling(2).min().reset_index(drop=True)

    df['macd_rising'] = df['macd_impulse'] < df['macd_histogram']
    df['ema_rising'] = df['ema_impulse'] < df[spine]

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
        print('Price action data was not found...')
        df['atr'] = None
        return

    if len(df) < window:
        df['atr'] = None
        return

    df['yest_close'] = df[['symbol', 'close']].groupby('symbol').shift(1).reset_index(drop=True)
    df['high_low_diff'] = df['high'] - df['low']
    df['high_close_diff'] = abs(df['yest_close'] - df['high'])
    df['low_close_diff'] = abs(df['yest_close'] - df['low'])
    df['pre_atr'] = df[['high_low_diff', 'high_close_diff', 'low_close_diff']].max(axis=1)

    df['atr'] = (
        df[['symbol', 'pre_atr']]
        .groupby('symbol')
        .rolling(window)
        .mean()
        .reset_index(drop=True)
        .round(3)
    )

    df.drop(columns=['yest_close', 'high_low_diff', 'high_close_diff', 'low_close_diff', 'pre_atr'], inplace=True)


def calculate_sma(
    df: pd.DataFrame,
    window: int = 50,
) -> None:
    """
    Calculate sma column for designated pd.DataFrame.

    :param df: Target pd.DataFrame
    :param window: Number of closing periods used in SMA calculation.
    """

    if 'close' not in df.columns or 'symbol' not in df.columns:
        raise ValueError('close/symbol data not found in target pd.DataFrame')

    df[f'sma_{window}'] = (
        df[['symbol', 'close']]
        .groupby('symbol')
        .rolling(window)
        .mean()
        .reset_index(drop=True)
        .round(2)
    )


def calculate_ema(
    df: pd.DataFrame,
    window: int,
) -> None:
    """
    Calculate ema column for designated pd.DataFrame.

    :param df: Target pd.DataFrame
    :param window: Number of closing periods used in EMA calculation.
    """

    if 'close' not in df.columns or 'symbol' not in df.columns:
        raise ValueError('close or symbol not found in target pd.DataFrame')

    df[f'ema_{window}'] = (
        df[['symbol', 'close']]
        .groupby(by='symbol')
        .ewm(span=window, adjust=False, min_periods=window)
        .mean()
        .reset_index(drop=True)
        .round(2)
    )


def calculate_macd(
    df: pd.DataFrame,
    short_window: int = 12,
    long_window: int = 26,
    signal_window: int = 9,
) -> None:
    """
    Calculate macd_histogram column for designated pd.DataFrame.

    :param df: Target pd.DataFrame
    :param short_window: Number of closing periods used to make the short window.
    :param long_window: Number of closing periods used to make the long window.
    :param signal_window: Number of (short_window - long_window) periods to make signal line.
    """

    if 'close' not in df.columns or 'symbol' not in df.columns:
        raise ValueError('close or symbol not found in target pd.DataFrame')

    df[f'ema_{short_window}'] = (
        df[['symbol', 'close']]
        .groupby(by='symbol')
        .ewm(span=short_window, adjust=False, min_periods=short_window)
        .mean()
        .reset_index(drop=True)
    )

    df[f'ema_{long_window}'] = (
        df[['symbol', 'close']]
        .groupby(by='symbol')
        .ewm(span=long_window, adjust=False, min_periods=long_window)
        .mean()
        .reset_index(drop=True)
    )

    df['fast_line'] = df[f'ema_{short_window}'] - df[f'ema_{long_window}']

    df['signal_line'] = (
        df[['symbol', 'fast_line']]
        .groupby(by='symbol')
        .ewm(span=signal_window, adjust=False, min_periods=signal_window)
        .mean()
        .reset_index(drop=True)
    )

    df['macd_histogram'] = round(df['fast_line'] - df['signal_line'], 7)
    df[['fast_line', 'signal_line']] = df[['fast_line', 'signal_line']].round(7)

    df.drop(columns=[f'ema_{short_window}', f'ema_{long_window}'], inplace=True)

from datetime import datetime, date, timedelta

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
        print('macd and/or ema spine was not found...')
        df['impulse'] = 'Red'
        return

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
        print('Price action data was not found...')
        df['atr'] = None
        return

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


def calculate_ema_start(
    df: pd.DataFrame,
    window: int,
    price_column: str = 'close',
) -> None:
    """
    Creates column label and calculates the starting value for an EMA window.

    :param df: Target pd.DataFrame
    :param window: Number of closing periods used in EMA
    :param price_column: Column to use when calculating EMA
    """

    if price_column not in df.columns or 'symbol' not in df.columns:
        raise ValueError('price column or symbol not found in dataframe')

    df[f'ema_{window}'] = df[['symbol', price_column]].groupby('symbol').rolling(window).mean().reset_index(drop=True).round(2)


def calculate_ema_end(
    df: pd.DataFrame,
    window: int,
    start_row: int,
    price_column: str = 'close',
) -> None:
    """
    Calculate EMA values, assuming there is a starting EMA value already.

    :param df: Target pd.DataFrame
    :param window: Number of closing periods used in EMA
    :param start_row: Designate where the EMA start value is, relative to symbol.
    :param price_column: Column to use when calculating EMA
    """

    if f'ema_{window}' not in df.columns or price_column not in df.columns or 'symbol' not in df.columns:
        raise ValueError('price column, symbol or relevant ema column not found in pd.DataFrame')

    if len(df) < 2:
        return

    smoothing_coeff = 2/(window + 1)

    symbol = df['symbol'][0]
    symbol_row = 1

    for row_index in range(len(df)):

        if df['symbol'][row_index] != symbol:
            symbol_row = 1
            symbol = df['symbol'][row_index]

        if symbol_row > start_row:
            previous_ema = df.loc[row_index - 1, f'ema_{window}']
            today_price = df.loc[row_index, price_column]

            df.loc[row_index, f'ema_{window}'] = (
                today_price * smoothing_coeff + previous_ema * (1 - smoothing_coeff)
            )

        symbol_row += 1

    df[f'ema_{window}'] = df[f'ema_{window}'].round(2)


def calculate_ema(
    df: pd.DataFrame,
    window: int,
    price_column: str = 'close',
) -> None:
    """
    Calculate entire EMA column for a designated df and window.

    :param df: Target pd.DataFrame
    :param window: Number of closing periods used in EMA
    :param price_column: Column to use when calculating EMA
    """

    calculate_ema_start(df=df, window=window, price_column=price_column)
    calculate_ema_end(df=df, window=window, start_row=window, price_column=price_column)


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

    if len(df) < long_window + signal_window:
        raise ValueError('Not enough periods to calculate macd column')

    calculate_ema(df=df, window=short_window)
    calculate_ema(df=df, window=long_window)
    df.dropna(subset=[f'ema_{short_window}', f'ema_{long_window}'], inplace=True)
    df.reset_index(drop=True, inplace=True)

    df['fast_line'] = df[f'ema_{short_window}'] - df[f'ema_{long_window}']

    calculate_ema(df=df, window=signal_window, price_column='fast_line')

    df['macd_histogram'] = round(df['fast_line'] - df[f'ema_{signal_window}'], 7)

    df.drop(columns=['fast_line', f'ema_{short_window}', f'ema_{long_window}', f'ema_{signal_window}'], inplace=True)

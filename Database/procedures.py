import sqlite3

import pandas as pd

from db_utils import get_missing_days, get_missing_weeks, DB_FILEPATH
from df_utils import calculate_ema_start, calculate_ema_end
from polygon_api import get_daily_market_snapshot, get_weekly_market_snapshot
from queries import update_sma_query, start_ema_query, end_ema_query


def update_daily_price_action() -> None:
    """
    Inserts price action values into daily DB table for missing days.
    """

    with sqlite3.connect(DB_FILEPATH) as conn:
        db_symbols_df = pd.read_sql_query(sql='SELECT symbol FROM symbols', con=conn)

    if db_symbols_df.empty:
        raise ValueError('No active symbols in database...')

    missing_day_list = get_missing_days()

    for missing_day in missing_day_list:
        snap_df = get_daily_market_snapshot(missing_day)

        if snap_df.empty:
            continue

        snap_df = snap_df.merge(db_symbols_df, on='symbol', how='inner')

        with sqlite3.connect(DB_FILEPATH) as conn:
            cursor = conn.cursor()
            cursor.executemany(
                'INSERT INTO daily (date, symbol, open, high, low, close, volume) VALUES(?, ?, ?, ?, ?, ?, ?);',
                snap_df.values
            )
            conn.commit()

        print(f'Daily {missing_day} loaded into DB')


def update_weekly_price_action() -> None:
    """
    Inserts price action values into weekly DB table for missing weeks.
    This procedure will always update the most recent week found in the DB,
    considering weekly trading periods are updated daily and may be incomplete.
    """

    with sqlite3.connect(DB_FILEPATH) as conn:
        db_symbols_df = pd.read_sql_query(sql='SELECT symbol FROM symbols', con=conn)

    if db_symbols_df.empty:
        raise ValueError('No active symbols in database...')

    missing_week_list = get_missing_weeks('weekly')

    for missing_week in missing_week_list:
        snap_df = get_weekly_market_snapshot(missing_week)

        if snap_df.empty:
            continue

        snap_df = snap_df.merge(db_symbols_df, on='symbol', how='inner')

        with sqlite3.connect(DB_FILEPATH) as conn:
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM weekly WHERE date = '{missing_week.strftime('%Y-%m-%d')}'")
            cursor.executemany('INSERT INTO weekly(date, symbol, open, high, low, close, volume) VALUES(?, ?, ?, ?, ?, ?, ?);',
                               snap_df.values)
            conn.commit()

        print(f'Week {missing_week} loaded into DB')


def update_sma(
    window: int,
    table: str,
) -> None:
    """
    Finds symbols in DB with enough data to calculate sma if they are NULL.
    Insert calculated SMA values into target SQL table.

    :param window: Target SMA column.
    :param table: Target table to update SMA values for.
    """

    conn = sqlite3.connect(DB_FILEPATH)

    df = pd.read_sql_query(sql=update_sma_query(window, table), con=conn)

    if df.empty:
        return

    df[f'sma_{window}'] = df[['symbol', 'close']].groupby('symbol').rolling(window).mean().reset_index(drop=True).round(2)
    df = df.dropna(subset=[f'sma_{window}']).filter(items=[f'sma_{window}', 'symbol', 'date'])

    cursor = conn.cursor()
    cursor.executemany(f'UPDATE {table} SET sma_{window} = ? WHERE symbol = ? AND date = ?', df.values)
    conn.commit()
    conn.close()

    print(f'{table} SMAs updated...')


def update_ema(
    window: int,
    table: str,
):
    """
    Finds symbols in DB with enough data to calculate ema if they are NULL.
    Insert calculated EMA values into target SQL table.

    :param window: Target EMA column.
    :param table: Target table to update EMA values for.
    """

    conn = sqlite3.connect(DB_FILEPATH)
    cursor = conn.cursor()

    start_df = pd.read_sql_query(sql=start_ema_query(window, table), con=conn)

    if not start_df.empty:

        calculate_ema_start(df=start_df, window=window)
        start_df = start_df.dropna(subset=[f'ema_{window}']).filter(items=[f'ema_{window}', 'symbol', 'date'])

        cursor.executemany(f'UPDATE {table} SET ema_{window} = ? WHERE symbol = ? AND date = ?', start_df.values)
        conn.commit()

    end_df = pd.read_sql_query(sql=end_ema_query(window, table), con=conn)

    if not end_df.empty:

        calculate_ema_end(df=end_df, window=window, start_row=1)
        end_df = end_df.filter(items=[f'ema_{window}', 'symbol', 'date'])

        cursor.executemany(f'UPDATE {table} SET ema_{window} = ? WHERE symbol = ? AND date = ?', end_df.values)
        conn.commit()

    conn.close()

    print(f'{table} EMA_{window}s updated...')

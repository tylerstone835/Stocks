import sqlite3

import pandas as pd

from db_utils import get_missing_days, get_missing_weeks, DB_FILEPATH
from polygon_api import get_daily_market_snapshot, get_weekly_market_snapshot


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

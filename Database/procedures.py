from datetime import datetime, date, timedelta
import sqlite3

import pandas as pd

from db_utils import get_missing_days, get_missing_weeks, DB_FILEPATH, insert_data
from df_utils import calculate_macd, calculate_ema, calculate_keltner_channels
from df_utils import calculate_atr, calculate_impulse, calculate_sma, calculate_date_table
from polygon_api import get_daily_market_snapshot, get_weekly_market_snapshot
from queries import *


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

    if table == 'weekly':
        clear_latest_value(table='weekly', column=f'sma_{window}')

    conn = sqlite3.connect(DB_FILEPATH)

    df = pd.read_sql_query(sql=update_sma_query(window, table), con=conn)

    if df.empty:
        return

    calculate_sma(df=df, window=window)
    df = df.dropna(subset=[f'sma_{window}']).filter(items=[f'sma_{window}', 'symbol', 'date'])

    cursor = conn.cursor()
    cursor.executemany(f'UPDATE {table} SET sma_{window} = ? WHERE symbol = ? AND date = ?', df.values)
    conn.commit()
    conn.close()

    print(f'{table} SMAs updated...')


def update_ema(
    window: int,
    table: str,
    record_offset: int = 200,
):
    """
    Updates symbols with enough data to calculate missing ema values.

    :param window: Target EMA column.
    :param table: Target table to update EMA values for.
    :param record_offset: Max number of records included in EMA calculation.
    """

    if table == 'weekly':
        clear_latest_value(table='weekly', column=f'ema_{window}')

    con = sqlite3.connect(DB_FILEPATH)
    cursor = con.cursor()

    df = pd.read_sql_query(con=con, sql=update_ema_query(table=table, window=window, record_offset=record_offset))

    if df.empty:
        return

    calculate_ema(df=df, window=window)

    df = (
        df[~(df[f'ema_{window}'].isna()) & (df['current_ema'].isna())]
        .drop(columns=['close', 'current_ema'])
        .filter(items=[f'ema_{window}', 'symbol', 'date'])
    )

    cursor.executemany(f'UPDATE {table} SET ema_{window} = ? WHERE symbol = ? AND date = ?', df.values)
    con.commit()
    con.close()

    print(f'{table} ema_{window}s updated...')


def update_macd(
    table: str,
    short_window: int = 12,
    long_window: int = 26,
    signal_window: int = 9,
    record_offset: int = 200,
) -> None:
    """
    Finds symbols in DB with enough data to calculate macd if they are NULL.
    Insert calculated MACD values into target SQL table.

    :param table: Target table to update MACD values for.
    :param short_window: Size of short window in MACD calculation.
    :param long_window: Size of long window in MACD calculation.
    :param signal_window: Size of signal window in MACD calculation.
    :param record_offset: Max number of records included in EMA calculation.
    """

    if table == 'weekly':
        clear_latest_value(table='weekly', column='macd_histogram')

    con = sqlite3.connect(DB_FILEPATH)
    cursor = con.cursor()

    df = pd.read_sql_query(
        con=con,
        sql=update_macd_query(
            table=table,
            record_minimum=long_window + signal_window - 1,
            record_offset=record_offset
            )
    )

    if df.empty:
        return

    calculate_macd(df=df, short_window=short_window, long_window=long_window, signal_window=signal_window)

    df = (df[~(df['macd_histogram'].isna()) & (df['current_macd'].isna())]
          .drop(columns=['close', 'current_macd'])
          .filter(items=['macd_histogram', 'symbol', 'date']))

    cursor.executemany(f'UPDATE {table} SET macd_histogram = ? WHERE symbol = ? AND date = ?', df.values)
    con.commit()
    con.close()

    print(f'{table} macd_histograms updated...')


def update_keltner(
    table: str,
    ema_spine_window: int = 20,
    channel_window: int = 125,
) -> None:
    """
    Finds symbols in DB with enough data to calculate keltner if they are NULL.
    Insert calculated keltner values into target SQL table.

    :param table: Target table to update keltner values for.
    :param ema_spine_window: ema indicator to base deviation calculations on.
    :param channel_window: Number of periods included in 95th deviation percentile.
    """

    if table == 'weekly':
        clear_latest_value(table='weekly', column='deviation')
        clear_latest_value(table='weekly', column='upper_channel')
        clear_latest_value(table='weekly', column='lower_channel')

    con = sqlite3.connect(DB_FILEPATH)
    cursor = con.cursor()

    df = pd.read_sql_query(
        con=con,
        sql=update_keltner_query(
            table=table,
            ema_spine_window=ema_spine_window,
            channel_window=channel_window
            )
    )

    if df.empty:
        return

    calculate_keltner_channels(df=df, spine=f'ema_{ema_spine_window}', window=channel_window)

    df = (df[~(df['deviation'].isna()) & (df['current_deviation'].isna())]
          .drop(columns=['low', 'high', f'ema_{ema_spine_window}', 'current_deviation']))

    cursor.executemany(
        f'UPDATE {table} SET deviation = ? WHERE symbol = ? AND date = ?',
        df[['deviation', 'symbol', 'date']].values
    )

    cursor.executemany(
        f'UPDATE {table} SET upper_channel = ? WHERE symbol = ? AND date = ?',
        df[['upper_channel', 'symbol', 'date']].values
    )

    cursor.executemany(
        f'UPDATE {table} SET lower_channel = ? WHERE symbol = ? AND date = ?',
        df[['lower_channel', 'symbol', 'date']].values
    )

    con.commit()
    con.close()

    print(f'{table} keltner values updated...')


def update_atr(
    table: str,
    window: int = 14,
) -> None:
    """
    Finds symbols in DB with enough data to calculate atr if they are NULL.
    Insert calculated atr values into target SQL table.

    :param table: Target table to update atr values for.
    :param window: Number of periods to include in atr calculation.
    """

    if table == 'weekly':
        clear_latest_value(table='weekly', column='atr')

    con = sqlite3.connect(DB_FILEPATH)
    cursor = con.cursor()

    df = pd.read_sql_query(con=con, sql=update_atr_query(table=table, window=window))

    if df.empty:
        return

    calculate_atr(df=df, window=window)

    df = (df[(df['current_atr'].isna()) & ~(df['atr'].isna())]
          .filter(items=['atr', 'symbol', 'date']))

    cursor.executemany(f'UPDATE {table} SET atr = ? WHERE symbol = ? AND date = ?', df.values)
    con.commit()
    con.close()

    print(f'{table} ATRs updated...')


def update_impulse(
    table: str,
    spine: str = 'ema_10',
) -> None:
    """
    Finds symbols in DB with enough data to calculate impulse if they are NULL.
    Insert calculated impulse values into target SQL table.

    :param table: Target table to update impulse values for.
    :param spine: Indicator column to use as impulse reference.
    """

    if table == 'weekly':
        clear_latest_value(table='weekly', column='impulse')

    con = sqlite3.connect(DB_FILEPATH)
    cursor = con.cursor()

    df = pd.read_sql_query(con=con, sql=update_impulse_query(table=table, spine=spine))

    if df.empty:
        return

    calculate_impulse(df=df, spine=spine)

    df = df[(df['current_impulse'].isna()) & ~(df['impulse'].isna())].filter(items=['impulse', 'symbol', 'date'])

    cursor.executemany(f'UPDATE {table} SET impulse = ? WHERE symbol = ? AND date = ?', df.values)
    con.commit()
    con.close()

    print(f'{table} impulse updated...')


def clear_latest_value(
    table: str,
    column: str,
) -> None:
    """
    Sets the latest designated column that is not null, to null.
    Useful for clearing out latest Weekly value, for when it needs
    to be recalculated as the week progresses.

    :param table: Target table.
    :param column: Target column.
    """

    con = sqlite3.connect(DB_FILEPATH)
    cursor = con.cursor()

    df = pd.read_sql_query(con=con, sql=clear_latest_value_query(table, column))

    if df.empty:
        return

    df[column] = None
    df = df.filter(items=[column, 'symbol', 'date'])

    cursor.executemany(f'UPDATE {table} SET {column} = ? WHERE symbol = ? AND date = ?', df.values)
    con.commit()
    con.close()


def update_calendar_table() -> None:
    """
    Identify if there are any missing days between the date of runtime
    and the latest date found in the calendar table. If days are missing,
    insert them into the calendar SQL table.
    """

    with sqlite3.connect(DB_FILEPATH) as con:
        cursor = con.cursor()
        result = cursor.execute("SELECT MAX(date) FROM calendar")

    if not result:
        raise ValueError('No records found in calendar/date table.')

    latest_db_date = datetime.strptime(result.fetchone()[0], '%Y-%m-%d').date()
    today = date.today()

    if latest_db_date == today or latest_db_date > today:
        return

    missing_days_df = calculate_date_table(start=latest_db_date + timedelta(days=1), end=today)
    insert_data(missing_days_df, table_name='calendar')

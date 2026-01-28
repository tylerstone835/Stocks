import os
import sqlite3

import pandas as pd


class Symbol:

    def __init__(
        self,
        symbol: str,
        lookback_years: float = 5,
    ):
        self.symbol = symbol
        self.lookback_years = lookback_years

        self.daily_row_index = 0
        self.daily_trend = None
        self.daily_macd_min = None
        self.daily_macd_max = None
        self.daily_channel_status = None

        self.weekly_row_index = 0
        self.weekly_trend = None
        self.weekly_macd_min = None
        self.weekly_macd_max = None
        self.weekly_channel_status = None

        with sqlite3.connect(os.environ.get('STOCK_DATABASE')) as con:

            # _____________ Initialize weekly dataframe _____________

            self.weekly_df = (
                pd.read_sql_query(
                    con=con,
                    sql=f"""
                        SELECT
                            *,
                            '' as season
                        FROM
                            weekly
                        WHERE
                            symbol = '{self.symbol}'
                            AND date >= date('now', '-{int(self.lookback_years * 365)} day')
                        ORDER BY
                            date
                        """,
                    dtype={
                        'date': 'datetime64[ns]',
                        'symbol': 'string',
                        'open': 'float',
                        'high': 'float',
                        'low': 'float',
                        'close': 'float',
                        'volume': 'float',
                        'ema_5': 'float',
                        'ema_10': 'float',
                        'ema_20': 'float',
                        'fast_line': 'float',
                        'signal_line': 'float',
                        'macd_histogram': 'float',
                        'deviation': 'float',
                        'upper_channel': 'float',
                        'lower_channel': 'float',
                        'atr': 'float',
                        'impulse': 'string',
                        'season': 'string'
                    }
                )
                .assign(yest_macd = lambda df: df['macd_histogram'].shift(1))
                .dropna(subset=['upper_channel'])
                .reset_index(drop=True)
            )
            self.weekly_df.loc[lambda df: (df['macd_histogram'] <= 0) & (df['macd_histogram'] <= df['yest_macd']), ['season']] = 'Winter'
            self.weekly_df.loc[lambda df: (df['macd_histogram'] < 0) & (df['macd_histogram'] > df['yest_macd']), ['season']] = 'Spring'
            self.weekly_df.loc[lambda df: (df['macd_histogram'] >= 0) & (df['macd_histogram'] >= df['yest_macd']), ['season']] = 'Summer'
            self.weekly_df.loc[lambda df: (df['macd_histogram'] > 0) & (df['macd_histogram'] < df['yest_macd']), ['season']] = 'Autumn'

            # _____________ Initialize weekly dataframe _____________

            self.daily_df = (
                pd.read_sql_query(
                    con=con,
                    sql=f"""
                        SELECT
                            *,
                            '' as season
                        FROM
                            daily
                        WHERE
                            symbol = '{self.symbol}'
                            AND date >= date('now', '-{int(self.lookback_years * 365)} day')
                        ORDER BY
                            date
                        """,
                    dtype={
                        'date': 'datetime64[ns]',
                        'symbol': 'string',
                        'open': 'float',
                        'high': 'float',
                        'low': 'float',
                        'close': 'float',
                        'volume': 'float',
                        'sma_50': 'float',
                        'ema_5': 'float',
                        'ema_10': 'float',
                        'ema_20': 'float',
                        'fast_line': 'float',
                        'signal_line': 'float',
                        'macd_histogram': 'float',
                        'deviation': 'float',
                        'upper_channel': 'float',
                        'lower_channel': 'float',
                        'atr': 'float',
                        'impulse': 'string',
                        'season': 'string'
                    }
                )
                .assign(yest_macd = lambda df: df['macd_histogram'].shift(1))
                .dropna(subset=['upper_channel'])
                .loc[lambda df: df['date'] >= self.weekly_df['date'].min()]
                .reset_index(drop=True)
            )
            self.daily_df.loc[lambda df: (df['macd_histogram'] <= 0) & (df['macd_histogram'] <= df['yest_macd']), ['season']] = 'Winter'
            self.daily_df.loc[lambda df: (df['macd_histogram'] < 0) & (df['macd_histogram'] > df['yest_macd']), ['season']] = 'Spring'
            self.daily_df.loc[lambda df: (df['macd_histogram'] >= 0) & (df['macd_histogram'] >= df['yest_macd']), ['season']] = 'Summer'
            self.daily_df.loc[lambda df: (df['macd_histogram'] > 0) & (df['macd_histogram'] < df['yest_macd']), ['season']] = 'Autumn'


    # __________________________________________________ Navigation __________________________________________________
    def increment_daily(
        self,
        distance: int = 1
    ):
        if self.daily_row_index + distance > self.daily_df.index.max():
            print(f'Daily index {self.daily_row_index + distance}/{self.daily_df.index.max()} out of bounds...')
            return

        self.daily_row_index += distance


    def increment_weekly(
        self,
        distance: int = 1
    ):
        if self.weekly_row_index + distance > self.weekly_df.index.max():
            print(f'Weekly index {self.weekly_row_index + distance}/{self.weekly_df.index.max()} out of bounds...')
            return

        self.weekly_row_index += distance


    def fast_forward_daily(
        self,
        months: float,
    ):
        current_date = self.daily_df.at[self.daily_row_index, 'date']
        timedelta = pd.Timedelta(int(30 * months), 'days')
        new_index = self.daily_df.loc[lambda df: df['date'] >= current_date + timedelta].index.min()

        if pd.isna(new_index):
            print(f'Attempted to fast forward to {(current_date + timedelta).date()}. Not in daily DataFrame...')
            return

        self.daily_row_index = new_index


    def fast_forward_weekly(
        self,
        months: float,
    ):
        current_date = self.weekly_df.at[self.weekly_row_index, 'date']
        timedelta = pd.Timedelta(int(30 * months), 'days')
        new_index = self.weekly_df.loc[lambda df: df['date'] <= current_date + timedelta].index.max()

        if pd.isna(new_index):
            print(f'Attempted to fast forward to {(current_date + timedelta).date()}. Not in weekly DataFrame...')
            return

        self.weekly_row_index = new_index


    def synchronize_daily(
        self,
    ):

        current_weekly_date = self.weekly_df.at[self.weekly_row_index, 'date']
        new_daily_index = self.daily_df.loc[lambda df: df['date'] >= current_weekly_date].index.min()

        if pd.isna(new_daily_index):
            print(f'Attempted to synchronize to {current_weekly_date.date()}. Not in daily DataFrame...')
            return

        self.daily_row_index = new_daily_index


    def synchronize_weekly(
        self,
    ):

        current_daily_date = self.daily_df.at[self.daily_row_index, 'date']
        new_weekly_index = self.weekly_df.loc[lambda df: df['date'] <= current_daily_date].index.max()

        if pd.isna(new_weekly_index):
            print(f'Attempted to synchronize to {current_daily_date.date()}. Not in weekly DataFrame...')
            return

        self.weekly_row_index = new_weekly_index


    # __________________________________________________ Attribute Updates __________________________________________________
    def set_daily_trend(
        self,
    ):
        if self.daily_df.empty:
            return

        row = self.daily_df.loc[self.daily_row_index, ['ema_10', 'ema_20']]

        if row.ema_10 > row.ema_20:
            self.daily_trend = 'Bullish'
        elif row.ema_10 < row.ema_20:
            self.daily_trend = 'Bearish'
        else:
            self.daily_trend = None


    def set_weekly_trend(
        self,
    ):
        if self.weekly_df.empty:
            return

        row = self.weekly_df.loc[self.weekly_row_index, ['ema_10', 'ema_20']]

        if row.ema_10 > row.ema_20:
            self.weekly_trend = 'Bullish'
        elif row.ema_10 < row.ema_20:
            self.weekly_trend = 'Bearish'
        else:
            self.weekly_trend = None

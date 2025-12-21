import os

import pandas as pd
import sqlite3


class Symbol:

    def __init__(self, symbol):

        self.symbol = symbol

        with sqlite3.connect(os.environ.get('STOCK_DATABASE')) as con:
            self.data = pd.read_sql_query(
                con=con,
                sql=f"""
                SELECT
                    *
                FROM
                    daily
                WHERE
                    symbol = '{self.symbol}'
                    AND upper_channel IS NOT NULL
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
                    'volume': 'int',
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
                    'impulse': 'string'
                }
            )

        self.row = 0
        self.get_trend()
        self.get_channel_status()
        self.get_macd_extremes()
        self.get_value_status()
        self.get_impulse_status()


    def __str__(self):
        return (
            f'Symbol | {self.symbol}\n'
            f'Trend | {self.trend}\n'
            f'Channel Status | {self.channel_status}\n'
            f'Shape | {self.data.shape}\n'
            f'Current Row | {self.row}\n'
            f'Min MACD | {self.min_macd}\n'
            f'Max MACD | {self.max_macd}'
        )


    def __iter__(self):
        self.row = self.data.loc[lambda df: df['date'] >= df['date'].min() + pd.Timedelta(days=30 * 6)].head(1).index[0]
        self.get_trend()
        self.get_channel_status()
        self.get_macd_extremes()
        self.get_value_status()
        self.get_impulse_status()
        return self


    def __next__(self):
        if self.row < self.data.shape[0] - 1:
            self.row += 1
            self.get_trend()
            self.get_channel_status()
            self.get_macd_extremes()
            self.get_value_status()
            self.get_impulse_status()
        else:
            raise StopIteration


    def get_trend(self):
        df = self.data.loc[self.row]

        if df.ema_5 > df.ema_10 > df.ema_20:
            self.trend = 'Bullish'
        elif df.ema_5 < df.ema_10 < df.ema_20:
            self.trend = 'Bearish'
        else:
            self.trend = None


    def get_channel_status(self):
        df = self.data.loc[self.row]

        if df.low < df.lower_channel or df.high > df.upper_channel:
            self.channel_status = 'Penetrated'
        else:
            self.channel_status = None


    def get_macd_extremes(self):

        macd_df = (
            self.data
            .loc[
                lambda df: (df['date'] < self.data.loc[self.row, 'date']) &
                (df['date'] >= self.data.loc[self.row, 'date'] - pd.Timedelta(days=30 * 6))
            ]
            ['macd_histogram']
        )

        self.min_macd = macd_df.min()
        self.max_macd = macd_df.max()


    def get_value_status(self):
        df = self.data.loc[self.row]

        pa_max = df[['open', 'high', 'low', 'close']].max()
        pa_min = df[['open', 'high', 'low', 'close']].min()

        ema_max = df[['ema_10', 'ema_20']].max()
        ema_min = df[['ema_10', 'ema_20']].min()

        self.value_status = max(pa_min, ema_min) <= min(pa_max, ema_max)


    def get_impulse_status(self):

        if self.row == 0:
            self.impulse_status = None
            return

        df = self.data

        current_impulse = df.loc[self.row, 'impulse']
        yest_impulse = df.loc[self.row - 1, 'impulse']

        if self.trend == 'Bullish' and yest_impulse == 'Red' and current_impulse != 'Red':
            self.impulse_status = 'Resuming'
        elif self.trend == 'Bearish' and yest_impulse == 'Green' and current_impulse != 'Green':
            self.impulse_status = 'Resuming'
        else:
            self.impulse_status = None


symbol = Symbol('LEG')
for period in symbol:
    print(symbol.impulse_status)

import os

import matplotlib.pyplot as plt
import pandas as pd
import sqlite3

from chart_utils import plot_standard_chart, shade_entry


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

        self.index_dict = dict()
        self.row = 0
        self.logic_index = 0
        self.generated_plots = 0
        self.get_trend()
        self.get_channel_status()
        self.get_macd_extremes()
        self.get_value_status()
        self.get_impulse_status()


    def __str__(self):
        return (
            f'Symbol | {self.symbol}\n'
            f'Date | {self.data.loc[self.row, 'date'].date()}\n'
            f'Trend | {self.trend}\n'
            f'Channel Status | {self.channel_status}\n'
            f'Shape | {self.data.shape}\n'
            f'Current Row | {self.row}\n'
            f'Current MACD | {self.current_macd}\n'
            f'Min MACD | {self.min_macd}\n'
            f'Max MACD | {self.max_macd}\n'
            f'Value Status | {self.value_status}\n'
            f'Impulse Status | {self.impulse_status}\n'
            f'Logic Index | {self.logic_index}\n'
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
                lambda df: (df['date'] <= self.data.loc[self.row, 'date']) &
                (df['date'] >= self.data.loc[self.row, 'date'] - pd.Timedelta(days=30 * 6))
            ]
            ['macd_histogram']
        )

        self.current_macd = self.data.loc[self.row, 'macd_histogram']
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


    def log_index(self):
        if self.logic_index not in self.index_dict:
            self.index_dict[self.logic_index] = self.data.loc[self.row, 'date'].date().strftime('%Y-%m-%d')


    def reset_index(self):
        self.index_dict = dict()


    def promote(
        self,
        increment: int = 1
    ):
        self.logic_index += increment
        self.log_index()


    def demote(
        self,
        increment: int
    ):
        self.logic_index -= increment
        self.reset_index()


    def plot_data(
        self,
        fmonths: int = 6,
        bmonths: int = 6
    ):
        df = self.data
        current_date = df.loc[self.row, 'date']

        df = df.loc[
            (df['date'] >= current_date - pd.Timedelta(days=30 * bmonths)) &
            (df['date'] <= current_date + pd.Timedelta(days=30 * fmonths))
        ].reset_index(drop=True)

        fig, ax = plt.subplots(
            nrows=3,
            ncols=1,
            sharex=True,
            height_ratios=[.73, .07, .2],
            figsize=(20, 10)
        )
        df['date'] = df['date'].astype('string')
        plot_standard_chart(axes=ax, df=df, xticks=pd.Series([i for i in self.index_dict.values()]))
        shade_entry(df=df, entry=current_date, n_periods=20, ax=ax[0])

        plt.tight_layout()
        plt.savefig(f'/home/tst/python/Stocks/Charts/Strategies/{self.symbol}_{self.generated_plots}.png')
        plt.close()

        self.generated_plots += 1

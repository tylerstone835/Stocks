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

        self.daily_macd_min = None
        self.daily_macd_max = None
        self.daily_trigger_index = 0

        self.weekly_macd_min = None
        self.weekly_macd_max = None
        self.weekly_trigger_index = 0
        self.weekly_annotations = []

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

            self.weekly_row_index = 0
            self.weekly_range = range(0, self.weekly_df.shape[0])
            self.set_weekly()

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

            self.daily_row_index = 0
            self.daily_range = range(0, self.daily_df.shape[0])
            self.set_daily()


    # __________________________________________________ Navigation __________________________________________________
    def increment_daily(
        self,
        distance: int = 1
    ) -> None:
        if self.daily_row_index + distance > self.daily_df.index.max():
            print(f'Daily index {self.daily_row_index + distance}/{self.daily_df.index.max()} out of bounds...')
            return

        self.daily_row_index += distance
        self.set_daily()


    def increment_weekly(
        self,
        distance: int = 1
    ) -> None:
        if self.weekly_row_index + distance > self.weekly_df.index.max():
            print(f'Weekly index {self.weekly_row_index + distance}/{self.weekly_df.index.max()} out of bounds...')
            return

        self.weekly_row_index += distance
        self.set_weekly()


    def ff_daily(
        self,
        months: float,
    ) -> None:
        current_date = self.daily_df.at[self.daily_row_index, 'date']
        timedelta = pd.Timedelta(int(30 * months), 'days')
        new_index = self.daily_df.loc[lambda df: df['date'] >= current_date + timedelta].index.min()

        if pd.isna(new_index):
            print(f'Attempted to fast forward to {(current_date + timedelta).date()}. Not in daily DataFrame...')
            return

        self.daily_row_index = new_index
        self.set_daily()


    def ff_weekly(
        self,
        months: float,
    ) -> None:
        current_date = self.weekly_df.at[self.weekly_row_index, 'date']
        timedelta = pd.Timedelta(int(30 * months), 'days')
        new_index = self.weekly_df.loc[lambda df: df['date'] <= current_date + timedelta].index.max()

        if pd.isna(new_index):
            print(f'Attempted to fast forward to {(current_date + timedelta).date()}. Not in weekly DataFrame...')
            return

        self.weekly_row_index = new_index
        self.set_weekly()


    def sync_daily(
        self,
    ) -> None:

        current_weekly_date = self.weekly_df.at[self.weekly_row_index, 'date']
        new_daily_index = self.daily_df.loc[lambda df: df['date'] >= current_weekly_date].index.min()

        if pd.isna(new_daily_index):
            print(f'Attempted to synchronize to {current_weekly_date.date()}. Not in daily DataFrame...')
            return

        self.daily_row_index = new_daily_index
        self.set_daily()


    def sync_weekly(
        self,
    ) -> None:

        current_daily_date = self.daily_df.at[self.daily_row_index, 'date']
        new_weekly_index = self.weekly_df.loc[lambda df: df['date'] <= current_daily_date].index.max()

        if pd.isna(new_weekly_index):
            print(f'Attempted to synchronize to {current_daily_date.date()}. Not in weekly DataFrame...')
            return

        self.weekly_row_index = new_weekly_index
        self.set_weekly()


    # ____________________________________________________ Calculations ____________________________________________________
    def calculate_trend(
        self,
        series_row: pd.Series,
    ) -> str | None:
        if series_row.ema_10 > series_row.ema_20:
            return 'Bullish'
        elif series_row.ema_10 < series_row.ema_20:
            return 'Bearish'
        else:
            return None


    def calculate_channel_status(
        self,
        series_row: pd.Series,
    ) -> str | None:
        if series_row.high > series_row.upper_channel or series_row.low < series_row.lower_channel:
            return 'Penetrated'
        else:
            return None


    def calculate_macd_extremes(
        self,
        df: pd.DataFrame,
        row_index: int,
        lookback_months: int,
    ) -> tuple:
        current_date = df.at[row_index, 'date']
        time_delta = pd.Timedelta(days=30 * lookback_months)

        macd_df = df[['date', 'macd_histogram']].loc[
            (df['date'] <= current_date) &
            (df['date'] >= current_date - time_delta)
        ]

        return macd_df['macd_histogram'].min(), macd_df['macd_histogram'].max()


    def calculate_value_status(
        self,
        series_row: pd.Series,
    ) -> bool:

        pa_max = series_row[['open', 'high', 'low', 'close']].max()
        pa_min = series_row[['open', 'high', 'low', 'close']].min()

        ema_max = series_row[['ema_10', 'ema_20']].max()
        ema_min = series_row[['ema_10', 'ema_20']].min()

        return max(pa_min, ema_min) <= min(pa_max, ema_max)



    # __________________________________________________ Setters __________________________________________________
    def set_daily(
        self,
    ) -> None:
        self.set_daily_row()
        self.set_daily_trend()
        self.set_daily_channel_status()
        self.set_daily_macd_extremes()
        self.set_daily_value_status()


    def set_weekly(
        self,
    ) -> None:
        self.set_weekly_row()
        self.set_weekly_trend()
        self.set_weekly_channel_status()
        self.set_weekly_macd_extremes()
        self.set_weekly_value_status()


    def set_daily_row(
        self,
    ) -> None:
        if self.daily_df.empty:
            return

        self.daily_row = self.daily_df.loc[self.daily_row_index]


    def set_weekly_row(
        self,
    ) -> None:
        if self.weekly_df.empty:
            return

        self.weekly_row = self.weekly_df.loc[self.weekly_row_index]


    def set_daily_trend(
        self,
    ) -> None:
        if self.daily_df.empty:
            return

        self.daily_trend = self.calculate_trend(self.daily_row)

        if self.daily_trend == 'Bullish':
            self.daily_cooldown_season = 'Spring'

        elif self.daily_trend == 'Bearish':
            self.daily_cooldown_season = 'Autumn'

        else:
            self.daily_cooldown_season = None


    def set_weekly_trend(
        self,
    ) -> None:
        if self.weekly_df.empty:
            return

        self.weekly_trend = self.calculate_trend(self.weekly_row)

        if self.weekly_trend == 'Bullish':
            self.weekly_cooldown_season = 'Spring'

        elif self.weekly_trend == 'Bearish':
            self.weekly_cooldown_season = 'Autumn'

        else:
            self.weekly_cooldown_season = None



    def set_daily_channel_status(
        self,
    ) -> None:
        if self.daily_df.empty:
            return

        self.daily_channel_status = self.calculate_channel_status(self.daily_row)


    def set_weekly_channel_status(
        self,
    ) -> None:
        if self.weekly_df.empty:
            return

        self.weekly_channel_status = self.calculate_channel_status(self.weekly_row)


    def set_daily_macd_extremes(
        self,
    ) -> None:
        if self.daily_df.empty:
            return

        self.daily_macd_min, self.daily_macd_max = self.calculate_macd_extremes(
            df=self.daily_df,
            row_index=self.daily_row_index,
            lookback_months=3
        )


    def set_weekly_macd_extremes(
        self,
    ) -> None:
        if self.weekly_df.empty:
            return

        self.weekly_macd_min, self.weekly_macd_max = self.calculate_macd_extremes(
            df = self.weekly_df,
            row_index = self.weekly_row_index,
            lookback_months = 15
        )


    def set_daily_value_status(
        self,
    ) -> None:
        if self.daily_df.empty:
            return

        self.daily_value_status = self.calculate_value_status(self.daily_row)


    def set_weekly_value_status(
        self,
    ) -> None:
        if self.weekly_df.empty:
            return

        self.weekly_value_status = self.calculate_value_status(self.weekly_row)


    # __________________________________________________ Methods __________________________________________________
    def inc_daily_trigger(
        self,
        amount: int = 1,
    ) -> None:
        self.daily_trigger_index += amount


    def inc_weekly_trigger(
        self,
        amount: int = 1,
    ) -> None:
        self.weekly_trigger_index += amount

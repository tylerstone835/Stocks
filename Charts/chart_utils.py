import matplotlib.pyplot as plt
import pandas as pd


def plot_macd(
    axes: plt.axes,
    df: pd.DataFrame,
    xticks: list|pd.Series = [],
) -> None:
    """
    Plot MACD histogram on child axes. This plot needs an aditional day of price action
    to determine the color of beginning MACD bar. Chart this first as it will truncate the
    extra bar after use.

    :param axes: Child axes on matplotlib.pyplot.figure
    :param df: Source pd.DataFrame. Requires macd, impulse and date data.
    :param xticks: Add a custom series of date xticks, else blank.
    """

    if not {'macd_histogram', 'impulse', 'date'} <= set(df.columns):
        raise ValueError('Missing necessary data to construct chart')

    # MACD bar colors
    NEGATIVE_RISING = '#9B4D4C'
    NEGATIVE_FALLING = '#720000'
    POSITIVE_RISING = '#0D0D0D'
    POSITIVE_FALLING = '#999999'

    # Create helper columns
    df['yest_hist'] = df['macd_histogram'].shift(1)
    df.dropna(subset=['yest_hist'], inplace=True)
    df.reset_index(drop=True, inplace=True)
    df['color'] = ''

    df.loc[(df['macd_histogram'] < 0) & (df['macd_histogram'] > df['yest_hist']), 'color'] = NEGATIVE_RISING
    df.loc[(df['macd_histogram'] < 0) & (df['macd_histogram'] <= df['yest_hist']), 'color'] = NEGATIVE_FALLING
    df.loc[(df['macd_histogram'] > 0) & (df['macd_histogram'] >= df['yest_hist']), 'color'] = POSITIVE_RISING
    df.loc[(df['macd_histogram'] > 0) & (df['macd_histogram'] < df['yest_hist']), 'color'] = POSITIVE_FALLING

    # _______________________________________ MACD Histogram Chart _______________________________________
    axes.bar(x=df['date'], height=df['macd_histogram'], width=.5, color=df['color'], zorder=3)
    axes.grid(visible=True, linestyle=':', alpha=.4, zorder=0)
    axes.set_xticks(xticks)
    axes.set_xticklabels([])
    axes.set_yticklabels([])
    axes.tick_params(axis='x', direction='in', length=0)
    axes.tick_params(axis='y', direction='out', length=1.5)
    axes.set_xbound(lower=0, upper=len(df))

    df.drop(columns=['yest_hist', 'color'], inplace=True)


def plot_ohlc(
    axes: plt.axes,
    df: pd.DataFrame,
    xticks: list|pd.Series = [],
) -> None:
    """
    Plot OHLC chart on child axes. Requires OHLC data, all EMAs,
    Keltner Channels and Impulse data.

    :param axes: Child axes on matplotlib.pyplot.figure
    :param df: Source pd.DataFrame. Requires OHLC.
    :param xticks: Add a custom series of date xticks, else blank.
    """

    required_columns_set = {'date', 'open', 'high', 'low', 'close', 'ema_5', 'ema_10', 'ema_20',
                            'upper_channel', 'lower_channel', 'impulse'}

    if not required_columns_set <= set(df.columns):
        raise ValueError('Missing necessary data to construct chart')

    df['color'] = df['impulse'].map({'Green': '#004820', 'Blue': '#0000FF', 'Red': '#AC2E2E'})

    # _______________________________________ OHLC Chart _______________________________________
    axes.plot(df['date'], df['ema_5'], linestyle='-', color='red', linewidth=.2)
    axes.plot(df['date'], df['ema_10'], linestyle='-', color='black', linewidth=.4)
    axes.plot(df['date'], df['ema_20'], linestyle='-', color='black', linewidth=.8)
    axes.plot(df['date'], df['upper_channel'], linestyle='--', color='black', linewidth=.8)
    axes.plot(df['date'], df['lower_channel'], linestyle='--', color='black', linewidth=.8)

    for i in range(len(df)):
        date = df['date'][i]
        high = df['high'][i]
        low = df['low'][i]
        open = df['open'][i]
        close = df['close'][i]
        color = df['color'][i]

        axes.plot([date, date], [low, high], marker=',', linestyle='-', color=color, linewidth=.75)
        axes.plot(date, open, marker=0, color=color, markersize=1.5)
        axes.plot(date, close, marker=1, color=color, markersize=1.5)

    axes.set_xbound(lower=0, upper=len(df))
    axes.grid(visible=True, linestyle=':', alpha=.4, zorder=0)
    axes.set_xticks(xticks)
    axes.set_xticklabels([])
    axes.tick_params(axis='x', direction='in', length=0)
    axes.tick_params(axis='y', direction='out', length=1.5)

    df.drop(columns=['color'], inplace=True)

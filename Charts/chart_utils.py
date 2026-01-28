import io
import os

from cairosvg import svg2png
import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image
import requests


GRID_ALPHA = .7

def plot_macd(
    axes: plt.axes,
    df: pd.DataFrame,
    xticks: pd.Series = pd.Series(),
) -> None:
    """
    Plot MACD histogram on child axes. This plot needs an aditional day of price action
    to determine the color of beginning MACD bar. Chart this first as it will truncate the
    extra bar after use.

    :param axes: Child axes on matplotlib.pyplot.figure
    :param df: Source pd.DataFrame. Requires macd, impulse and date data.
    :param xticks: Add a custom series of date xticks, else blank.
    """

    if not {'macd_histogram', 'fast_line', 'signal_line', 'impulse', 'date'} <= set(df.columns):
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
    axes.grid(visible=True, linestyle=':', alpha=GRID_ALPHA, zorder=0)
    axes.set_xticks(xticks)
    axes.set_xticklabels([])
    axes.set_yticklabels([])
    axes.tick_params(axis='x', direction='in', length=0)
    axes.tick_params(axis='y', direction='out', length=1.5)


    line_axes = axes.twinx()
    line_axes.plot(df['date'], df['fast_line'], linestyle='-', color='k', linewidth=.4)
    line_axes.plot(df['date'], df['signal_line'], linestyle='-', color='k', linewidth=.8)
    line_axes.set_yticks([])

    axes.set_xbound(lower=-.5, upper=len(df) - .5)
    line_axes.set_xbound(lower=-.5, upper=len(df) - .5)

    df.drop(columns=['yest_hist', 'color'], inplace=True)


def plot_ohlc(
    axes: plt.axes,
    df: pd.DataFrame,
    xticks: pd.Series = pd.Series(),
) -> None:
    """
    Plot OHLC chart on child axes. Requires OHLC data, all EMAs,
    Keltner Channels and Impulse data.

    :param axes: Child axes on matplotlib.pyplot.figure
    :param df: Source pd.DataFrame. Requires OHLC.
    :param xticks: Add a custom series of date xticks, else blank.
    """

    required_columns_set = {'date', 'open', 'high', 'low', 'close', 'ema_5', 'ema_10',
                            'ema_20', 'upper_channel', 'lower_channel', 'impulse'}

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

    axes.grid(visible=True, linestyle=':', alpha=GRID_ALPHA, zorder=0)
    axes.set_xticks(xticks)
    axes.set_xticklabels([fdate.date().strftime('%b-%y') for fdate in xticks.astype('datetime64[ns]')])
    axes.tick_params(axis='x', direction='in', length=0)
    axes.tick_params(axis='y', direction='out', length=1.5)
    axes.set_xbound(lower=-.5, upper=len(df) - .5)

    df.drop(columns=['color'], inplace=True)


def plot_volume(
    axes: plt.axes,
    df: pd.DataFrame,
    xticks: pd.Series = pd.Series(),
) -> None:
    """
    Plot bar chart of volume data on child axes.

    :param axes: Child axes on matplotlib.pyplot.figure
    :param df: Source pd.DataFrame. Requires Volume.
    :param xticks: Add a custom series of date xticks, else blank.
    """

    if not {'date', 'volume'} <= set(df.columns):
        raise ValueError('Missing necessary data to construct chart')

    axes.bar(
        x=df['date'],
        height=df['volume'],
        color='#720000',
        width=.5
    )

    axes.set_xbound(lower=-.5, upper=len(df) - .5)
    axes.grid(visible=True, linestyle=':', alpha=GRID_ALPHA, zorder=0)
    axes.set_xticks(xticks)
    axes.set_xticklabels([])
    axes.set_yticklabels([])
    axes.tick_params(axis='x', direction='in', length=0)
    axes.tick_params(axis='y', direction='out', length=1.5)


def overlay_image(
    fig: plt.figure,
    image_url: str | None,
    image_height: int = 50,
    image_alpha: float = .3,
) -> None:
    """
    Overlay logo on parent figure.

    :param fig: Parent figure.
    :param image_url: Massive image url.
    :param image_height: Height to scale image dims to.
    :param image_alpha: Image transparency.
    """

    if not image_url:
        print('No image provided')
        return

    api_key = os.environ.get('POLYGON_API_KEY')

    response = requests.get('/'.join([image_url, f'?apiKey={api_key}']))

    if response.status_code != 200:
        print('Failed to retrieve image')
        return

    file_extension = image_url.split('.')[-1]

    try:
        image_bytes = svg2png(response.content) if file_extension == 'svg' else response.content
    except:
        print('Response content failed to convert')
        return

    with Image.open(io.BytesIO(image_bytes)) as img:
        # Scale image so height is 50 px and convert to grayscale
        new_width = image_height * img.size[0] // img.size[1]
        img = img.resize(size=(new_width, image_height)).convert(mode='LA')

        # Calculate fig height in px to determine logo placement
        image_offset = fig.dpi * fig.get_figheight() - img.size[1] - 25
        fig.figimage(img, 55, image_offset, zorder=10, alpha=image_alpha)


def plot_standard_chart(
    axes: plt.axes,
    df: pd.DataFrame,
    xticks: pd.Series = pd.Series(),
) -> None:

    plot_macd(
        axes=axes[2],
        df=df,
        xticks=xticks
    )

    plot_volume(
        axes=axes[1],
        df=df,
        xticks=xticks
    )

    plot_ohlc(
        axes=axes[0],
        df=df,
        xticks=xticks
    )


def shade_entry(
    n_periods: int,
    entry: str,
    df: pd.DataFrame,
    ax: plt.axes,
) -> None:

    if not {'date', 'upper_channel', 'lower_channel'} <= set(df.columns):
        raise ValueError('Missing required fields to shade plot area...')

    shade_df = df
    shade_df['date'] = shade_df['date'].astype('datetime64[ns]')

    current_index = shade_df.loc[shade_df['date'] == entry].index[0]

    if current_index + n_periods > shade_df.shape[0] - 1:
        end_index = shade_df.shape[0] - 1
    else:
        end_index = current_index + n_periods

    end_date = shade_df.loc[end_index, 'date']

    shade_df['where'] = (shade_df['date'] >= entry) & (shade_df['date'] <= end_date)

    shade_df['date'] = shade_df['date'].astype('string')


    ax.fill_between(x=shade_df['date'], y1=shade_df['lower_channel'], y2=shade_df['upper_channel'], where=shade_df['where'], alpha=.25)
    ax.set_xbound(lower=-.5, upper=len(shade_df) - .5)

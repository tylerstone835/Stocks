import asyncio
import os

import aiohttp
import pandas as pd

POLYGON_API_KEY = os.environ.get('POLYGON_API_KEY')


async def get_price_action(
    session: aiohttp.ClientSession,
    ticker: str = 'MSFT',
    multiplier: int = 1,
    timespan: str = 'day',
    from_: str = '1970-01-01',
    to: str = '3000-01-01',
) -> pd.DataFrame:
    """
    Asynchronous coroutine that retrieves custom price action aggregations for
    a designated ticker, timespan, period.

    :param session: Asynchronous http client.
    :param ticker: Ticker symbol for a publicly traded stock.
    :param multiplier: Designated size of timespan (e.g., 1 day, 10 minute, 25 second).
    :param timespan: Size of time window (e.g., day, week, month).
    :param from_: Start of desired date period. Default to Unix start time to capture all.
    :param to: End of desired date period.
    :return: pd.DataFrame containing price action and volume for designated ticker.
    """

    path = f'/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from_}/{to}?apiKey={POLYGON_API_KEY}'
    response = await session.get(path)

    if response.status != 200:
        print('API call failed...')
        return pd.DataFrame()

    return pd.DataFrame((await response.json())['results']).assign(symbol=ticker)


async def gather_price_action(
    *ticker_batch,
    multiplier: int = 1,
    timespan: str = 'day',
    from_: str = '1970-01-01',
    to: str = '3000-01-01',
) -> pd.DataFrame:
    """
    Using get_price_action(), gather price action dataframes asynchronously.

    :param *ticker_batch: Tickers to gather price action data for.
    :param multiplier: Designated size of timespan (e.g., 1 day, 10 minute, 25 second).
    :param timespan: Size of time window (e.g., day, week, month).
    :param from_: Start of desired date period. Default to Unix start time to capture all.
    :param to: End of desired date period.
    :return: pd.DataFrame containing price action and volume for designated ticker.
    """
    async with aiohttp.ClientSession('https://api.polygon.io') as session:
        df_array = await asyncio.gather(
            *[get_price_action(session, ticker, multiplier, timespan, from_, to)
              for ticker in ticker_batch]
        )

    return (pd.concat(df_array)
            .rename(columns={'v': 'volume',
                             'o': 'open',
                             'h': 'high',
                             'l': 'low',
                             'c': 'close',
                             't': 'timestamp'})
            .filter(items=['timestamp',
                           'symbol',
                           'open',
                           'high',
                           'low',
                           'close',
                           'volume']))


async def get_sma(
    session: aiohttp.ClientSession,
    ticker: str = 'MSFT',
    timespan: str = 'day',
    window: int = 10,
    timestamp_gte: str = '1970-01-01',
) -> pd.DataFrame:
    """
    Asynchronous coroutine that retrieves simple moving average data for a designated
    ticker, timespan, window and date period.

    :param session: Asynchronous http client.
    :param ticker: Ticker symbol for a publicly traded stock.
    :param timespan: Size of time window (e.g., day, week, month).
    :param window: The number of periods used in SMA calculation.
    :param timestamp_gte: Starting date for SMA data.
    :return: pd.DataFrame containing SMA indicator data for designated ticker.
    """

    path = f'/v1/indicators/sma/{ticker}?timespan={timespan}&window={window}&limit=5000&timestamp.gte={timestamp_gte}&apiKey={POLYGON_API_KEY}'

    response = await session.get(path)
    if response.status != 200:
        print('API call failed...')
        return pd.DataFrame()

    if 'values' not in (await response.json())['results']:
        print(f'No SMA values found for {ticker}')
        return pd.DataFrame()

    return pd.DataFrame((await response.json())['results']['values']).assign(symbol=ticker)


async def gather_sma(
    *ticker_batch,
    timespan: str = 'day',
    window: int = 10,
    timestamp_gte: str = '1970-01-01',
) -> pd.DataFrame:
    """
    Using get_sma(), gather price action dataframes asynchronously.

    :param *ticker_batch: Tickers to gather price action data for.
    :param timespan: Size of time window (e.g., day, week, month).
    :param window: The number of periods used in SMA calculation.
    :param timestamp_gte: Starting date for SMA data.
    :return: pd.DataFrame containing SMA indicator data for designated ticker.
    """
    async with aiohttp.ClientSession('https://api.polygon.io') as session:
        df_array = await asyncio.gather(
            *[get_sma(session, ticker, timespan, window, timestamp_gte)
              for ticker in ticker_batch]
        )

    return (pd.concat(df_array)
            .assign(value=lambda x: x.value.round(2))
            .rename(columns={'value': f'sma_{window}'}))


async def get_ema(
    session: aiohttp.ClientSession,
    ticker: str = 'MSFT',
    timespan: str = 'day',
    window: int = 10,
    timestamp_gte: str = '1970-01-01',
) -> pd.DataFrame:
    """
    Asynchronous coroutine that retrieves exponential moving average data for a designated
    ticker, timespan, window and date period.

    :param session: Asynchronous http client.
    :param ticker: Ticker symbol for a publicly traded stock.
    :param timespan: Size of time window (e.g., day, week, month).
    :param window: The number of periods used in SMA calculation.
    :param timestamp_gte: Starting date for SMA data.
    :return: pd.DataFrame containing EMA indicator data for designated ticker.
    """

    path = f'/v1/indicators/ema/{ticker}?timespan={timespan}&window={window}&limit=5000&timestamp.gte={timestamp_gte}&apiKey={POLYGON_API_KEY}'

    response = await session.get(path)
    if response.status != 200:
        print('API call failed...')
        return pd.DataFrame()

    if 'values' not in (await response.json())['results']:
        print(f'No EMA values found for {ticker}')
        return pd.DataFrame()

    return pd.DataFrame((await response.json())['results']['values']).assign(symbol=ticker)


async def gather_ema(
    *ticker_batch,
    timespan: str = 'day',
    window: int = 10,
    timestamp_gte: str = '1970-01-01',
) -> pd.DataFrame:
    """
    Using get_ema(), gather price action dataframes asynchronously.

    :param *ticker_batch: Tickers to gather price action data for.
    :param timespan: Size of time window (e.g., day, week, month).
    :param window: The number of periods used in SMA calculation.
    :param timestamp_gte: Starting date for SMA data.
    :return: pd.DataFrame containing EMA indicator data for designated ticker.
    """
    async with aiohttp.ClientSession('https://api.polygon.io') as session:
        df_array = await asyncio.gather(
            *[get_ema(session, ticker, timespan, window, timestamp_gte)
              for ticker in ticker_batch]
        )

    return (pd.concat(df_array)
            .assign(value=lambda x: x.value.round(2))
            .rename(columns={'value': f'ema_{window}'}))

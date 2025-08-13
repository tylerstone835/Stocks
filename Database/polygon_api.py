import asyncio
from datetime import date
import os

import aiohttp
import pandas as pd
from polygon import RESTClient

from table_maps import overview_map

POLYGON_API_KEY = os.environ.get('POLYGON_API_KEY')
client = RESTClient()

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
        # print('API call failed...')
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
        # print('API call failed...')
        return pd.DataFrame()

    if 'values' not in (await response.json())['results']:
        # print(f'No SMA values found for {ticker}')
        return pd.DataFrame()

    return pd.DataFrame((await response.json())['results']['values']).assign(symbol=ticker)


async def gather_sma(
    *ticker_batch,
    timespan: str = 'day',
    window: int = 10,
    timestamp_gte: str = '1970-01-01',
) -> pd.DataFrame:
    """
    Using get_sma(), gather SMA dataframes asynchronously.

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
        # print('API call failed...')
        return pd.DataFrame()

    if 'values' not in (await response.json())['results']:
        # print(f'No EMA values found for {ticker}')
        return pd.DataFrame()

    return pd.DataFrame((await response.json())['results']['values']).assign(symbol=ticker)


async def gather_ema(
    *ticker_batch,
    timespan: str = 'day',
    window: int = 10,
    timestamp_gte: str = '1970-01-01',
) -> pd.DataFrame:
    """
    Using get_ema(), gather EMA dataframes asynchronously.

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


async def get_macd(
    session: aiohttp.ClientSession,
    ticker: str = 'MSFT',
    timespan: str = 'day',
    timestamp_gte: str = '1970-01-01',
) -> pd.DataFrame:
    """
    Asynchronous coroutine that retrieves moving average convergence/divergence data
    for a designated ticker, timespan, window and date period.

    :param session: Asynchronous http client.
    :param ticker: Ticker symbol for a publicly traded stock.
    :param timespan: Size of time window (e.g., day, week, month).
    :param timestamp_gte: Starting date for MACD data.
    :return: pd.DataFrame containing MACD indicator data for designated ticker.
    """

    path = f'/v1/indicators/macd/{ticker}?timespan={timespan}&limit=5000&timestamp.gte={timestamp_gte}&apiKey={POLYGON_API_KEY}'

    response = await session.get(path)
    if response.status != 200:
        # print('API call failed...')
        return pd.DataFrame()

    if 'values' not in (await response.json())['results']:
        # print(f'No MACD values found for {ticker}')
        return pd.DataFrame()

    return pd.DataFrame((await response.json())['results']['values']).assign(symbol=ticker)


async def gather_macd(
    *ticker_batch,
    timespan: str = 'day',
    timestamp_gte: str = '1970-01-01',
) -> pd.DataFrame:
    """
    Using get_macd(), gather MACD dataframes asynchronously.

    :param *ticker_batch: Tickers to gather price action data for.
    :param timespan: Size of time window (e.g., day, week, month).
    :param timestamp_gte: Starting date for SMA data.
    :return: pd.DataFrame containing MACD indicator data for designated ticker.
    """
    async with aiohttp.ClientSession('https://api.polygon.io') as session:
        df_array = await asyncio.gather(
            *[get_macd(session, ticker, timespan, timestamp_gte)
              for ticker in ticker_batch]
        )

    return (pd.concat(df_array)
            .assign(histogram=lambda x: x.histogram.round(7))
            .rename(columns={'histogram': 'macd_histogram'})
            .filter(items=['timestamp', 'symbol', 'macd_histogram']))


async def get_overview(
    session: aiohttp.ClientSession,
    ticker: str = 'MSFT',
) -> pd.DataFrame:
    """
    Asynchronous coroutine that retrieves basic company information.

    :param session: Asynchronous http client.
    :param ticker: Ticker symbol for a publicly traded stock.
    :return: pd.DataFrame containing company overview data for designated ticker.
    """

    path = f'/v3/reference/tickers/{ticker}?apiKey={POLYGON_API_KEY}'

    response = await session.get(path)
    if response.status != 200:
        print('API call failed...')
        return pd.DataFrame()

    if 'results' not in (await response.json()):
        print(f'No overview found for {ticker}')
        return pd.DataFrame()

    return (await response.json())['results']


async def gather_overview(
    *ticker_batch
) -> pd.DataFrame:
    """
    Using get_overview(), gather overview dataframes asynchronously.

    :param *ticker_batch: Tickers to gather overview data for.
    :return: pd.DataFrame containing overview data for designated ticker.
    """
    async with aiohttp.ClientSession('https://api.polygon.io') as session:
        df_array = await asyncio.gather(
            *[get_overview(session, ticker) for ticker in ticker_batch]
        )

    return (pd.json_normalize(df_array)
            .rename(columns={
                        'ticker': 'symbol',
                        'share_class_shares_outstanding': 'outstanding_shares',
                        'branding.logo_url': 'logo_url'}
                    )
            .filter(items=[column for column in overview_map]))


def get_active_tickers(
    ticker_type: str = 'CS',
    market: str = 'stocks',
    batch_size: int = 50,
) -> list[str]:
    """
    Cross-references tickers listed as active in Polygon database and tickers traded
    on the most recent market day. Symbols can be listed as active by Polygon, but
    not be actively traded on the market.

    :param ticker_type: Ticker type to return (e.g., CS, ETF, INDEX)
    :param market: Market type to evaluate (e.g., stocks, crypto, indices).
    :param batch_size: Number of elements in sublist (batches).
    :return: List of active, recently traded ticker symbols in designated market/type.
    """

    # Retrieve series containing common stocks with an active status.
    response_body = client.list_tickers(type=ticker_type, market=market, limit=1000, active=True)
    active_series = pd.DataFrame([response for response in response_body])['ticker']

    # Return series containing stocks traded on the most recent trading day.
    today = date.today()

    response = client.get_grouped_daily_aggs(date=today, market_type=market)
    while not response:
        today = today - timedelta(days=1)
        response = client.get_grouped_daily_aggs(date=today, market_type=market)
    recent_series = pd.DataFrame(response)['ticker']

    ticker_list = (
        pd.merge(
            left=active_series,
            right=recent_series,
            how='inner',
            on='ticker'
        )
        .drop_duplicates()
        ['ticker']
        .to_list()
    )

    return [ticker_list[i: i + batch_size] for i in range(0, len(ticker_list), batch_size)]

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
    *ticker_batch
) -> pd.DataFrame:
    """
    Using get_price_action(), gather price action dataframes asynchronously.

    :param *ticker_batch: Tickers to gather price action data for.
    """
    async with aiohttp.ClientSession('https://api.polygon.io') as session:
        df_array = await asyncio.gather(
            *[get_price_action(session, ticker) for ticker in ticker_batch]
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

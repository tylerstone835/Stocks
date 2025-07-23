import pandas as pd
from polygon import RESTClient
from polygon.exceptions import BadResponse

from utils import natural_join

client = RESTClient()


def get_price_action(
    ticker: str = 'MSFT',
    multiplier: int = 1,
    timespan: str = 'day',
    from_: str = '1970-01-01',
    to: str = '3000-01-01'
    ) -> pd.DataFrame:
    """
    Returns a pd.DataFrame containing the price action and volume for a designated
    ticker, timespan and date period.

    :param ticker: Ticker symbol for a publicly traded stock.
    :param multiplier: Designated size of timespan (e.g., 1 day, 10 minute, 25 second).
    :param timespan: Size of time window (e.g., day, week, month).
    :param from_: Start of desired date period. Default to Unix start time to capture all.
    :param to: End of desired date period.
    :return: pd.DataFrame containing price action and volume for designated ticker.
    """

    try:
        response = client.get_aggs(ticker=ticker,
                                   multiplier=multiplier,
                                   timespan=timespan,
                                   from_=from_,
                                   to=to
                                   )
    except BadResponse:
        print('API call failed...')
        return pd.DataFrame()

    if not response:
        print(f'Price action not found for {ticker}')
        return pd.DataFrame()

    return (
        pd.DataFrame(response)
        .assign(ticker=ticker)
        .filter(items=['timestamp', 'ticker', 'open', 'high', 'low', 'close', 'volume'])
        .astype(dtype={'ticker': 'string'})
    )


def get_sma(
    ticker: str = 'MSFT',
    timespan: str = 'day',
    window: int = 10,
    timestamp_gte: str = '1970-01-01'
    ) -> pd.DataFrame:
    """
    Returns a pd.DataFrame containing the simple moving average data for a designated ticker,
    timespan, window and date period.

    :param ticker: Ticker symbol for a publicly traded stock.
    :param timespan: Size of time window (e.g., day, week, month).
    :param window: The number of periods used in SMA calculation.
    :param timestamp_gte: Starting date for SMA data.
    :return: pd.DataFrame containing SMA indicator data for designated ticker.
    """

    try:
        response = client.get_sma(
            ticker=ticker,
            timespan=timespan,
            window=window,
            timestamp_gte=timestamp_gte
        )

    except BadResponse:
        print('API call failed...')
        return pd.DataFrame()

    if not response:
        print(f'SMA data not found for {ticker}')
        return pd.DataFrame()

    return (
        pd.DataFrame(response.values)
        .assign(ticker=ticker)
        .rename(columns={'value': f'sma_{window}'})
        .filter(items=['timestamp', 'ticker', f'sma_{window}'])
        .astype(dtype={'ticker': 'string'})
    )


if __name__ == '__main__':
    df = get_price_action()
    print(df.head())
    df = get_sma()

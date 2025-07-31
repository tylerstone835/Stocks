from datetime import date, timedelta

import pandas as pd
from polygon import RESTClient
from polygon.exceptions import BadResponse


client = RESTClient()


def get_price_action(
    ticker: str = 'MSFT',
    multiplier: int = 1,
    timespan: str = 'day',
    from_: str = '1970-01-01',
    to: str = '3000-01-01',
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
    timestamp_gte: str = '1970-01-01',
    limit: int = 5000,
) -> pd.DataFrame:
    """
    Returns a pd.DataFrame containing the simple moving average data for a designated ticker,
    timespan, window and date period.

    :param ticker: Ticker symbol for a publicly traded stock.
    :param timespan: Size of time window (e.g., day, week, month).
    :param window: The number of periods used in SMA calculation.
    :param timestamp_gte: Starting date for SMA data.
    :param limit: Limit the number of results returned.
    :return: pd.DataFrame containing SMA indicator data for designated ticker.
    """

    try:
        response = client.get_sma(
            ticker=ticker,
            timespan=timespan,
            window=window,
            timestamp_gte=timestamp_gte,
            limit=limit
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


def get_ema(
    ticker: str = 'MSFT',
    timespan: str = 'day',
    window: int = 10,
    timestamp_gte: str = '1970-01-01',
    limit: int = 5000,
) -> pd.DataFrame:
    """
    Returns a pd.DataFrame containing the exponential moving average data for a designated ticker,
    timespan, window and date period.

    :param ticker: Ticker symbol for a publicly traded stock.
    :param timespan: Size of time window (e.g., day, week, month).
    :param window: The number of periods used in EMA calculation.
    :param timestamp_gte: Starting date for EMA data.
    :param limit: Limit the number of results returned.
    :return: pd.DataFrame containing EMA indicator data for designated ticker.
    """

    try:
        response = client.get_ema(
            ticker=ticker,
            timespan=timespan,
            window=window,
            timestamp_gte=timestamp_gte,
            limit=limit
        )

    except BadResponse:
        print('API call failed...')
        return pd.DataFrame()

    if not response:
        print(f'EMA data not found for {ticker}')
        return pd.DataFrame()

    return (
        pd.DataFrame(response.values)
        .assign(ticker=ticker)
        .rename(columns={'value': f'ema_{window}'})
        .filter(items=['timestamp', 'ticker', f'ema_{window}'])
        .astype(dtype={'ticker': 'string'})
    )


def get_macd(
    ticker: str = 'MSFT',
    timespan: str = 'day',
    short_window: int = 12,
    long_window: int = 26,
    signal_window: int = 9,
    timestamp_gte: str = '1970-01-01',
    limit: int = 5000,
) -> pd.DataFrame:
    """
    Returns a pd.DataFrame containing the moving average convergence/divergence data for a
    designated ticker, timespan, window and date period.

    :param ticker: Ticker symbol for a publicly traded stock.
    :param timespan: Size of time window (e.g., day, week, month).
    :param short_window: The short window size used to calculate the MACD data.
    :param long_window: The long window size used to calculate the MACD data
    :param signal_window: The window size used to calculate the MACD signal line
    :param timestamp_gte: Starting date for MACD data.
    :param limit: Limit the number of results returned.
    :return: pd.DataFrame containing MACD indicator data for designated ticker.
    """

    try:
        response = client.get_macd(
            ticker=ticker,
            timespan=timespan,
            short_window=short_window,
            long_window=long_window,
            signal_window=signal_window,
            timestamp_gte=timestamp_gte,
            limit=limit
        )

    except BadResponse:
        print('API call failed...')
        return pd.DataFrame()

    if not response:
        print(f'MACD data not found for {ticker}')
        return pd.DataFrame()

    return (
        pd.DataFrame(response.values)
        .assign(ticker=ticker)
        .rename(columns={'histogram': 'macd_histogram'})
        .filter(items=['timestamp', 'ticker', 'macd_histogram'])
        .astype(dtype={'ticker': 'string'})
    )


def get_active_tickers(
    type: str = 'CS',
    market: str = 'stocks',
) -> list[str]:
    """
    Cross-references tickers listed as active in Polygon database and tickers traded
    on the most recent market day. Symbols can be listed as active by Polygon, but
    not be actively traded on the market.

    :param type: Ticker type to return (e.g., CS, ETF, INDEX)
    :param market: Market type to evaluate (e.g., stocks, crypto, indices)
    :return: List of active, recently traded ticker symbols in designated market/type.
    """

    # Retrieve series containing common stocks with an active status.
    try:
        response_body = client.list_tickers(type=type, market=market, limit=1000, active=True)
    except BadResponse:
        print('API call failed...')
        return

    active_series = pd.DataFrame([response for response in response_body])['ticker']

    # Return series containing stocks traded on the most recent trading day.
    today = date.today()

    try:
        response = client.get_grouped_daily_aggs(date=today, market_type=market)
        while not response:
            today = today - timedelta(days=1)
            response = client.get_grouped_daily_aggs(date=today, market_type=market)
    except BadResponse:
        print('API call failed...')
        return

    recent_series = pd.DataFrame(response)['ticker']

    return (pd.merge(left=active_series,
                     right=recent_series,
                     how='inner',
                     on='ticker')
            .drop_duplicates())['ticker'].to_list()

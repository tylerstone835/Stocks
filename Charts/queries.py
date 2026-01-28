def price_action_query(
    symbol: str,
    table: str = 'daily',
    daily_lookback: int = 366,
) -> str:
    return f"""
            SELECT
                dly.date,
                dly.open,
                dly.high,
                dly.low,
                dly.close,
                dly.volume,
                dly.ema_5,
                dly.ema_10,
                dly.ema_20,
                dly.upper_channel,
                dly.lower_channel,
                dly.fast_line,
                dly.signal_line,
                dly.macd_histogram,
                dly.impulse,

                sym.logo_url
            FROM
                {table} dly
            INNER JOIN
                symbols sym
                    ON dly.symbol = sym.symbol
            WHERE
                dly.symbol = '{symbol}'
                AND dly.date >= date('now', '-{daily_lookback} day')
            ORDER BY
                dly.date
    """


def beginning_of_month_query(
    n_of_months: int = 12,
) -> str:
    return f"""
    SELECT
        year,
        month,
        min(date) AS 'BOM'
    FROM
        calendar
    WHERE
        day_of_week < 5
        AND NOT is_market_holiday
        AND date >= date('now', '-365 day')
    GROUP BY
        1,2
    ORDER BY
        3 DESC
    LIMIT {n_of_months}
    """


def qualifying_symbols_query(
    volume_gte: int = 100000,
    close_gte: int = 10,
    years_gte: int = 2,
) -> str:

    return f"""
    WITH CTE_YEARS_OLD
    AS
    (
    SELECT
        symbol
    FROM
        daily
    WHERE
        upper_channel IS NOT NULL
    GROUP BY
        1
    HAVING
        CAST(julianday(date('now', 'localtime')) - julianday(MIN(date)) AS INT) >= 365 * {years_gte}
    )

    ,CTE_AVG_METRICS
    AS
    (
    SELECT
        symbol
    FROM
        daily
    WHERE
        date >= date('now', '-365 day')
    GROUP BY
        1
    HAVING
        AVG(volume) >= {volume_gte}
        AND AVG(close) >= {close_gte}
    )

    SELECT
        *
    FROM
        CTE_YEARS_OLD

    INTERSECT

    SELECT
        *
    FROM
        CTE_AVG_METRICS
    """

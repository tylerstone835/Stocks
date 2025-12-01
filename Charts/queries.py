def price_action_query(
    symbol: str,
) -> str:
    return f"""
    SELECT
        date,
        open,
        high,
        low,
        close,
        volume,
        ema_5,
        ema_10,
        ema_20,
        upper_channel,
        lower_channel,
        fast_line,
        signal_line,
        macd_histogram,
        impulse
    FROM
        daily
    WHERE
        symbol = '{symbol}'
        AND date >= date('now', '-366 day')
    ORDER BY
        date
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


def qualifying_symbols(
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

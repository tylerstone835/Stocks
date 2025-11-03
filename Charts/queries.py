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
):
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
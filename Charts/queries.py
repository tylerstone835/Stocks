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

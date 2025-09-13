def update_sma_query(
    window: int,
    table: str,
) -> str:
    """
    Formats query for updating an SMA by a designated window.

    :param window: SMA window.
    :param table: Target table to calculate SMA values for.
    :return: Formatted query.
    """

    return f"""
    /*
    Return Stocks that have the minimum number of records required
    to calculate the desired SMA window.
    */
    WITH CTE_QUALIFYING_STOCKS
    AS
    (
    SELECT
        symbol
    FROM
        {table}
    GROUP BY
        symbol
    HAVING
        COUNT(*) >= {window}
    )

    /*
    Return base data necessary to calculate desired SMA/update records.
    Row number, relative to the stock symbol, is added to perform an
    offset later in the query.
    */
    ,CTE_SMA_DATA
    AS
    (
    SELECT
        date,
        symbol,
        close,
        sma_{window},
        row_number() OVER (PARTITION BY symbol) AS 'row'
    FROM
        {table}
    WHERE
        SYMBOL IN (SELECT * FROM CTE_QUALIFYING_STOCKS)
    ORDER BY
        symbol,
        date
    )

    /*
    Identifies the first blank SMA row AFTER the minimum records required to
    calculate. This first row number is then offset by the SMA window, providing
    the starting row for each ticker symbol, guaranteeing enough base data to
    calculate all missing SMA rows for each symbol.
    */
    ,CTE_ROW_REFERENCE
    AS
    (
    SELECT
        symbol,
        MIN(row) - {window} AS 'starting_row'
    FROM
        CTE_SMA_DATA
    WHERE
        sma_{window} IS NULL
        AND row >= {window}
    GROUP BY
        symbol
    )

    /*
    Return every qualifying stock with missing SMA data, along with enough previous records
    to calculate the missing values.
    */
    SELECT
        date,
        symbol,
        close,
        sma_{window}
    FROM
        CTE_SMA_DATA data
    WHERE
        row > (SELECT starting_row FROM CTE_ROW_REFERENCE ref WHERE data.symbol = ref.symbol)
    ORDER BY
        symbol,
        date;
    """


def start_ema_query(
    window: int,
    table: str,
) -> str:
    """
    Return the symbols that need their ema started (EMA's begin with an SMA
    before the rest can be calculated exponentially).

    :param window: EMA window.
    :param table: Target table to calculate EMA values for.
    :return: Formatted query.
    """

    return f"""
    /*
    Label Stock Data with row_numbers for future reference
    */
    WITH CTE_STOCK_DATA
    AS
    (
    SELECT
        date,
        symbol,
        close,
        ema_{window},
        row_number() OVER (PARTITION BY symbol) AS 'row'
    FROM
        {table}
    ORDER BY
        symbol,
        date
    )

    /*
    Find stocks that have an empty beginning value for the EMA window.
    */
    ,CTE_QUALIFYING_STOCKS
    AS
    (
    SELECT
        symbol
    FROM
        CTE_STOCK_DATA
    WHERE
        row = {window}
        AND ema_{window} IS NULL
    )

    /*
    Return the number of records necessary to calculate the beginning of the EMA
    */
    SELECT
        date,
        symbol,
        close
    FROM
        CTE_STOCK_DATA
    WHERE
        symbol IN (SELECT * FROM CTE_QUALIFYING_STOCKS)
        AND row <= {window}
    ORDER BY
        symbol,
        date
    """

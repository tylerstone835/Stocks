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


def end_ema_query(
    window: int,
    table: str,
) -> str:
    """
    Return the symbols that have their ema started, but have
    NULL values that need to be calculated.

    :param window: EMA window.
    :param table: Target table to calculate EMA values for.
    :return: Formatted query.
    """

    return f"""
    /*
    Return Stocks that have the minimum number of records required
    to calculate the end of desired EMA window.
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
        COUNT(*) > {window}
    )

    /*
    Return base data necessary to calculate desired EMA/update records.
    Row number, relative to the stock symbol, is added to perform an
    offset later in the query.
    */
    , CTE_RANKED_DATA
    AS
    (
    SELECT
        date,
        symbol,
        close,
        ema_{window},
        ROW_NUMBER() OVER (PARTITION BY symbol) AS 'row'
    FROM
        {table}
    WHERE
        symbol IN (SELECT * FROM CTE_QUALIFYING_STOCKS)
    ORDER BY
        symbol,
        date
    )
    /*
    Identifies the first blank EMA row AFTER the minimum records required to
    calculate. This first row number is then offset by one, guaranteeing
    enough base data to calculate all missing EMA rows for each symbol.
    */
    ,CTE_ROW_REFERENCE
    AS
    (
    SELECT
        symbol,
        MIN(row) - 1 AS 'starting_row'
    FROM
        CTE_RANKED_DATA
    WHERE
        row > {window}
        AND ema_{window} IS NULL
    GROUP BY
        symbol
    )

    /*
    Return every qualifying stock with missing SMA data, along with enough previous records
    to calculate the missing values.
    */
    SELECT
        data.date,
        data.symbol,
        data.close,
        data.ema_{window}
    FROM
        CTE_RANKED_DATA data
    INNER JOIN
        CTE_ROW_REFERENCE row_ref
            ON data.symbol = row_ref.symbol
    WHERE
       data.row >= row_ref.starting_row
    ORDER BY
        data.symbol,
        data.date;
    """


def update_macd_query(
    table: str,
    record_minimum: int = 34,
    record_offset: int = 110,
) -> str:
    """
    Return symbols with missing MACD values, along with the data
    required to calculate the missing values.

    :param table: Target table to calculate MACD values for.
    :param record_minimum: Minimum number of records to calculate MACD.
    :param record_offset: Max records included to help calculate missing values.
    :return: Formatted query.
    """

    return f"""
    /*
    Return Stocks that have the minimum number of records
    required to calculate macd_histogram values.
    */

    WITH CTE_QUALIFYING_STOCKS
    AS
    (
    SELECT
        symbol
    FROM
        {table}
    GROUP BY
        1
    HAVING
        COUNT(*) >= {record_minimum}
    )


    /*
    Return base data necessary to calculate new macd_histogram values.
    Row number, relative to the stock symbol, is added to perform an
    offset later in the query.
    */
    ,CTE_BASE_DATA
    AS
    (
    SELECT
        date,
        symbol,
        close,
        macd_histogram,
        ROW_NUMBER() OVER (PARTITION BY symbol) AS 'row'
    FROM
        {table}
    WHERE
        symbol IN (SELECT * FROM CTE_QUALIFYING_STOCKS)
    ORDER BY
        2,1
    )


    /*
    Identifies the first blank MACD row AFTER the minimum records required to
    calculate. This first row number is then offset, providing the starting row
    for each ticker symbol, guaranteeing enough base data to calculate all missing
    MACD rows for each symbol.
    */
    ,CTE_OFFSET_INDEX
    AS
    (
    SELECT
        symbol,
        MIN(row) - {record_offset} AS 'start_row'
    FROM
        CTE_BASE_DATA
    WHERE
        row >= {record_minimum}
        AND macd_histogram IS NULL
    GROUP BY
        1
    )

    /*
    Return every qualifying stock with missing MACD data, along with
    enough previous records to calculate the missing values.
    */

    SELECT
        base.date,
        base.symbol,
        base.close,
        base.macd_histogram
    FROM
        CTE_BASE_DATA base
    INNER JOIN
        CTE_OFFSET_INDEX offset
            ON base.symbol = offset.symbol
    WHERE
        base.row >= offset.start_row
    """

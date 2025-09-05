def update_sma_query(
    window: int,
    table: str
) -> str:
    """
    Formats query for updating an SMA by a designated window.

    :param window: SMA window.
    :param table: Target table to calculate SMA values for.
    :return: Formatted query.
    """

    return f"""
    /*
    Return Stocks that have the minimum number of records to calculate
    the desired SMA window.
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
    Return SMA Data with the respective row number so an offset
    can be added later.
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
    Identifies the first blank SMA row after the minimum required records
    required to calculate SMA. The first blank SMA record is then offset by
    the number of required rows for calculation, guaranteeing every blank
    SMA record has enough for calculation.
    */
    ,CTE_REFERENCE
    AS
    (
    SELECT
        symbol,
        MIN(row) - {window} AS 'max_row'
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
        row > (SELECT max_row FROM CTE_REFERENCE ref WHERE data.symbol = ref.symbol)
    ORDER BY
        symbol,
        date;
    """

import asyncio
import logging
import os

from polygon_api import *
from df_utils import *
from db_utils import *
from table_maps import *

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(
        level=logging.INFO,
        filename='create.log',
        filemode='w',
        format='%(asctime)s:%(levelname)s:%(name)s:%(funcName)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Create daily SQL table.
    create_table_from_map(
        map=daily_map,
        table_name='daily'
    )
    logger.info('Daily SQL table built')

    # Create weekly SQL table.
    create_table_from_map(
        map=weekly_map,
        table_name='weekly'
    )
    logger.info('Weekly SQL table built')

    # Create symbols SQL table.
    create_table_from_map(
        map=overview_map,
        table_name='symbols'
    )
    logger.info('Symbols SQL table built')

    # Create date_dimension SQL table.
    create_table_from_map(
        map=date_dimension_map,
        table_name='calendar'
    )
    logger.info('Date Dimension SQL table built')

    # Gather/Batch active stock symbols.
    ticker_batches = get_active_tickers(batch_size=50)
    number_of_batches = len(ticker_batches)

    for batch_number, batch in enumerate(ticker_batches, 1):

        # Gather/Calculate ticker data for batch and insert into daily SQL table.
        daily_df = natural_join(
            asyncio.run(gather_price_action(*batch)),
            asyncio.run(gather_sma(*batch, window=50)),
            asyncio.run(gather_ema(*batch, window=5)),
            asyncio.run(gather_ema(*batch, window=10)),
            asyncio.run(gather_ema(*batch, window=20)),
            asyncio.run(gather_macd(*batch))
        )

        daily_df_list = []
        for df in (daily_df[daily_df['symbol'] == symbol].copy()
                   for symbol in daily_df['symbol'].unique()):

            calculate_keltner_channels(df)
            calculate_atr(df)
            calculate_impulse(df)
            timestamp_to_date(df)

            if not df.empty:
                daily_df_list.append(df)

        insert_data(
            *daily_df_list,
            table_name='daily'
        )
        logger.info('Daily batch %s/%s loaded', batch_number, number_of_batches)

        # Gather/Calculate ticker data for batch and insert into weekly SQL table.
        weekly_df = natural_join(
            asyncio.run(gather_price_action(*batch, timespan='week')),
            asyncio.run(gather_ema(*batch, window=5, timespan='week')),
            asyncio.run(gather_ema(*batch, window=10, timespan='week')),
            asyncio.run(gather_ema(*batch, window=20, timespan='week')),
            asyncio.run(gather_macd(*batch, timespan='week'))
        )

        weekly_df_list = []
        for df in (weekly_df[weekly_df['symbol'] == symbol].copy()
                   for symbol in weekly_df['symbol'].unique()):

            calculate_keltner_channels(df, window=26)
            calculate_atr(df)
            calculate_impulse(df)
            timestamp_to_date(df, timespan='week')

            if not df.empty:
                weekly_df_list.append(df)

        insert_data(
            *weekly_df_list,
            table_name='weekly'
        )
        logger.info('Weekly batch %s/%s loaded', batch_number, number_of_batches)

        # Gather ticker data for batch and insert into overview SQL table.
        overview_df = asyncio.run(gather_overview(*batch))

        insert_data(
            overview_df,
            table_name='symbols'
        )
        logger.info('Overview batch %s/%s loaded', batch_number, number_of_batches)

    # Calculate date table and insert into date_dimension SQL table.
    date_table_df = calculate_date_table()
    insert_data(
        date_table_df,
        table_name='date_dimension'
    )
    logger.info('date_dimension table loaded')


if __name__ == '__main__':
    main()

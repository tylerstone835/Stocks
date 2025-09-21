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

    # Create SQL tables.
    sql_table_dict = {
        'daily': daily_map,
        'weekly': weekly_map,
        'symbols': overview_map,
        'calendar': date_dimension_map
    }
    for table_name, table_map in sql_table_dict.items():
        create_table_from_map(map=table_map, table_name=table_name)
        logger.info('%s SQL table built', table_name)

    # Batch active stock symbols.
    ticker_batches = get_active_tickers(batch_size=50)
    number_of_batches = len(ticker_batches)

    for batch_number, batch in enumerate(ticker_batches, 1):

        # _____________________________ daily table _____________________________
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

        # _____________________________ weekly table _____________________________
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

        # ________________________ symbols table ________________________
        # Gather ticker data for batch and insert into overview SQL table.
        overview_df = asyncio.run(gather_overview(*batch))

        insert_data(
            overview_df,
            table_name='symbols'
        )
        logger.info('Overview batch %s/%s loaded', batch_number, number_of_batches)

    # _______________________ calendar table _______________________
    # Calculate date table and insert into date_dimension SQL table.
    date_table_df = calculate_date_table()
    insert_data(
        date_table_df,
        table_name='date_dimension'
    )
    logger.info('date_dimension table loaded')


if __name__ == '__main__':
    main()

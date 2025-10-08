import logging

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
    sql_table_dict = {'daily': daily_map, 'weekly': weekly_map, 'symbols': overview_map, 'calendar': date_dimension_map}

    for table_name, table_map in sql_table_dict.items():
        create_table_from_map(map=table_map, table_name=table_name)
        logger.info('%s SQL table built', table_name)

    # Batch active stock symbols.
    ticker_batches = get_active_tickers(batch_size=50)
    number_of_batches = len(ticker_batches)

    for batch_number, batch in enumerate(ticker_batches, 1):
        # _____________________________ daily table _____________________________
        # Gather/Calculate ticker data for batch and insert into daily SQL table.
        daily_df = asyncio.run(gather_price_action(*batch))
        calculate_sma(daily_df, 50)
        calculate_ema(daily_df, 5)
        calculate_ema(daily_df, 10)
        calculate_ema(daily_df, 20)
        calculate_macd(daily_df)
        calculate_keltner_channels(daily_df)
        calculate_atr(daily_df)
        calculate_impulse(daily_df)
        timestamp_to_date(daily_df)

        insert_data(daily_df, table_name='daily')
        logger.info('Daily batch %s/%s loaded', batch_number, number_of_batches)

        # _____________________________ weekly table _____________________________
        # Gather/Calculate ticker data for batch and insert into weekly SQL table.
        weekly_df = asyncio.run(gather_price_action(*batch, timespan='week'))

        calculate_ema(weekly_df, 5)
        calculate_ema(weekly_df, 10)
        calculate_ema(weekly_df, 20)
        calculate_macd(weekly_df)
        calculate_keltner_channels(weekly_df, window=26)
        calculate_atr(weekly_df)
        calculate_impulse(weekly_df)
        timestamp_to_date(weekly_df, timespan='week')

        insert_data(weekly_df, table_name='weekly')
        logger.info('Weekly batch %s/%s loaded', batch_number, number_of_batches)

        # ________________________ symbols table ________________________
        # Gather ticker data for batch and insert into overview SQL table.
        overview_df = asyncio.run(gather_overview(*batch))

        insert_data(overview_df, table_name='symbols')
        logger.info('Overview batch %s/%s loaded', batch_number, number_of_batches)

    # _______________________ calendar table _______________________
    # Calculate date table and insert into date_dimension SQL table.
    date_table_df = calculate_date_table()

    insert_data(date_table_df, table_name='calendar')
    logger.info('date_dimension table loaded')


if __name__ == '__main__':
    main()

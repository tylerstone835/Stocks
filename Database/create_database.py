import os

from dataframe import build_df_from_map
from db_utils import create_db_table_from_map
from polygon_api import get_active_tickers
from table_maps import daily_table_map


def main():

    database_filepath = os.environ.get('STOCK_DATABASE')

    # Create database tables
    create_db_table_from_map(
        database_fp=database_filepath,
        map=daily_table_map,
        table_name='daily'
    )

    ticker_list = get_active_tickers()

    for ticker in ticker_list:
        daily_df = build_df_from_map(ticker=ticker, map=daily_table_map)


if __name__ == '__main__':
    main()
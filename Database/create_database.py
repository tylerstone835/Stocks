from polygon_api import get_active_tickers
from dataframe import build_df_from_map
from table_maps import daily_table_map
from db_utils import create_db_table_from_map

def main():

    # Create database tables
    create_db_table_from_map(
        map=daily_table_map,
        table_name='daily'
    )

    # ticker_list = get_active_tickers()
    #
    # for ticker in ticker_list:
    #     daily_df = build_df_from_map(ticker=ticker, map=daily_table_map)

if __name__ == '__main__':
    main()

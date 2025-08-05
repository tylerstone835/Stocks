import os

from dataframe import *
from db_utils import create_table_from_map, insert_data
from polygon_api import *
from table_maps import price_fact_map


def main():
    DB_FILEPATH = os.environ.get('STOCK_DATABASE')

    # Create daily SQL table.
    create_table_from_map(
        db_filepath=DB_FILEPATH,
        map=price_fact_map,
        table_name='daily'
    )

    # Create weekly SQL table.
    create_table_from_map(
        db_filepath=DB_FILEPATH,
        map=price_fact_map,
        table_name='weekly'
    )

    ticker_list = get_active_tickers()

    for ticker in ticker_list[:5]:

        # Construct daily pd.DataFrame for ticker and insert into table.
        daily_df = natural_join(
                       get_price_action(ticker=ticker),
                       get_sma(ticker=ticker, window=50),
                       get_ema(ticker=ticker, window=5),
                       get_ema(ticker=ticker, window=10),
                       get_ema(ticker=ticker, window=20),
                       get_macd(ticker=ticker)
                   )

        calculate_keltner_channels(daily_df)
        calculate_atr(daily_df)
        calculate_impulse(daily_df)
        timestamp_to_date(daily_df)

        insert_data(
            df=daily_df,
            table_name='daily',
            db_filepath=DB_FILEPATH
        )

        # Construct weekly pd.DataFrame for ticker and insert into table.
        weekly_df = natural_join(
                        get_price_action(ticker=ticker, timespan='week'),
                        get_sma(ticker=ticker, window=50, timespan='week'),
                        get_ema(ticker=ticker, window=5, timespan='week'),
                        get_ema(ticker=ticker, window=10, timespan='week'),
                        get_ema(ticker=ticker, window=20, timespan='week'),
                        get_macd(ticker=ticker, timespan='week')
                    )

        calculate_keltner_channels(weekly_df, window=26)
        calculate_atr(weekly_df)
        calculate_impulse(weekly_df)
        timestamp_to_date(weekly_df)

        insert_data(
            df=weekly_df,
            table_name='weekly',
            db_filepath=DB_FILEPATH
        )



if __name__ == '__main__':
    main()

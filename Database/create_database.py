import asyncio
import os

from polygon_api import *
from df_utils import *
from db_utils import create_table_from_map, insert_data
from table_maps import *


def main():
    db_filepath = os.environ.get('STOCK_DATABASE')

    # Create daily SQL table.
    create_table_from_map(
        db_filepath=db_filepath,
        map=daily_map,
        table_name='daily'
    )

    # Create weekly SQL table.
    create_table_from_map(
        db_filepath=db_filepath,
        map=weekly_map,
        table_name='weekly'
    )

    # Create symbols SQL table.
    create_table_from_map(
        db_filepath=db_filepath,
        map=overview_map,
        table_name='symbols'
    )

    ticker_batches = get_active_tickers(batch_size=50)

    # Gather/Calculate ticker data for batch and insert into daily SQL table.
    for batch_number, batch in enumerate(ticker_batches, 1):
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
            df.dropna(inplace=True)

            if not df.empty:
                daily_df_list.append(df)

        insert_data(
            df=pd.concat(daily_df_list),
            table_name='daily',
            db_filepath=db_filepath
        )

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
            timestamp_to_date(df)
            df.dropna(inplace=True)

            if not df.empty:
                weekly_df_list.append(df)

        insert_data(
            df=pd.concat(weekly_df_list),
            table_name='weekly',
            db_filepath=db_filepath
        )

        # Gather ticker data for batch and insert into overview SQL table.
        overview_df = asyncio.run(gather_overview(*batch))

        insert_data(
            df=overview_df,
            table_name='symbols',
            db_filepath=db_filepath
        )


if __name__ == '__main__':
    main()

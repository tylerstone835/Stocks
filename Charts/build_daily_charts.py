import os
import sqlite3

import matplotlib.pyplot as plt
import pandas as pd

from chart_utils import plot_macd, plot_ohlc, plot_volume, overlay_image
from queries import *


def main() -> None:
    # Remove existing daily charts
    image_dir = '/home/tst/python/Stocks/Charts/Daily'

    for image in os.listdir(image_dir):
        os.remove('/'.join([image_dir, image]))


    with sqlite3.connect(os.environ.get('STOCK_DATABASE')) as con:

        bom_df = pd.read_sql_query(
            con=con,
            sql=beginning_of_month_query()
        )

        symbols_df = pd.read_sql_query(
            con=con,
            sql=qualifying_symbols_query()
        )

        for symbol in symbols_df['symbol']:

            stock_data_df = pd.read_sql_query(
                con=con,
                sql=price_action_query(symbol),
                dtype={'date': 'string'}
            )

            fig, ax = plt.subplots(
                nrows=3,
                ncols=1,
                sharex=True,
                height_ratios=[.73, .07, .2],
                figsize=(20, 10)
            )

            plot_macd(
                axes=ax[2],
                df=stock_data_df,
                xticks=bom_df['BOM']
            )

            plot_volume(
                axes=ax[1],
                df=stock_data_df,
                xticks=bom_df['BOM']
            )

            plot_ohlc(
                axes=ax[0],
                df=stock_data_df,
                xticks=bom_df['BOM']
            )

            overlay_image(
                fig=fig,
                image_url = stock_data_df.loc[0, 'logo_url']
            )

            plt.tight_layout()
            plt.savefig(f'/home/tst/python/Stocks/Charts/Daily/{symbol}.png')
            plt.close()


if __name__ == '__main__':
    main()

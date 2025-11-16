import os
import sqlite3

import matplotlib.pyplot as plt
import pandas as pd

from chart_utils import plot_macd, plot_ohlc
from queries import *

with sqlite3.connect(os.environ.get('STOCK_DATABASE')) as con:
    stock_data_df = pd.read_sql_query(
        con=con,
        sql=price_action_query('LEG')
    )

    bom_df = pd.read_sql_query(
        con=con,
        sql=beginning_of_month_query()
    )

fig, ax = plt.subplots(
    nrows=2,
    ncols=1,
    sharex=True,
    height_ratios=[.8, .2],
    figsize=(20, 10)
)

plot_macd(
    axes=ax[1],
    df=stock_data_df,
    xticks=bom_df['BOM']
)

plot_ohlc(
    axes=ax[0],
    df=stock_data_df,
    xticks=bom_df['BOM']
)

plt.tight_layout()
plt.show()
#plt.savefig(f'Daily\\LEG.png')
#plt.close()

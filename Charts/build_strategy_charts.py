import os
import sqlite3

import pandas as pd

from queries import qualifying_symbols_query
from strategies import channel_resumption
from symbol import Symbol


with sqlite3.connect(os.environ.get('STOCK_DATABASE')) as con:
    symbol_df = pd.read_sql_query(
        con=con,
        sql=qualifying_symbols_query()
    )


for symbol in symbol_df['symbol']:
    channel_resumption(Symbol(symbol))

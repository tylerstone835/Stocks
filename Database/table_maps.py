from dataframe import timestamp_to_date
from polygon_api import *


daily_table_map = {
    'date': {
        'dtype': 'DATE',
        'constraint': 'PRIMARY KEY',
        'callable': timestamp_to_date,
        'params': None
    },
    'symbol': {
        'dtype': 'VARCHAR(10)',
        'constraint': 'PRIMARY KEY',
        'callable': None,
        'params': None
    },
    'open': {
        'dtype': 'NUMBER(20, 3)',
        'constraint': 'NOT NULL',
        'callable': get_price_action,
        'params': {'multiplier': 1, 'timespan': 'day'}
    },
    'high': {
        'dtype': 'NUMBER(20, 3)',
        'constraint': 'NOT NULL',
        'callable': None,
        'params': None
    },
    'low': {
        'dtype': 'NUMBER(20, 3)',
        'constraint': 'NOT NULL',
        'callable': None,
        'params': None
    },
    'close': {
        'dtype': 'NUMBER(20, 3)',
        'constraint': 'NOT NULL',
        'callable': None,
        'params': None
    },
    'volume': {
        'dtype': 'NUMBER(20, 3)',
        'constraint': 'NOT NULL',
        'callable': None,
        'params': None
    },
    'sma_50': {
        'dtype': 'NUMBER(20, 3)',
        'constraint': '',
        'callable': get_sma,
        'params': {'timespan': 'day', 'window': 50}
    },
    'ema_5': {
        'dtype': 'NUMBER(20, 3)',
        'constraint': '',
        'callable': get_ema,
        'params': {'timespan': 'day', 'window': 5}
    },
    'ema_10': {
        'dtype': 'NUMBER(20, 3)',
        'constraint': '',
        'callable': get_ema,
        'params': {'timespan': 'day', 'window': 10}
    },
    'ema_20': {
        'dtype': 'NUMBER(20, 3)',
        'constraint': '',
        'callable': get_ema,
        'params': {'timespan': 'day', 'window': 20}
    },
    'macd_histogram': {
        'dtype': 'NUMBER(20, 7)',
        'constraint': '',
        'callable': get_macd,
        'params': {'timespan': 'day'}
    },
    'deviation': {
        'dtype': 'NUMBER(20, 4)',
        'constraint': '',
        'callable': None,
        'params': None
    },
    'upper_channel': {
        'dtype': 'NUMBER(20, 2)',
        'constraint': '',
        'callable': None,
        'params': None
    },
    'lower_channel': {
        'dtype': 'NUMBER(20, 2)',
        'constraint': '',
        'callable': None,
        'params': None
    },
    'atr': {
        'dtype': 'NUMBER(20, 2)',
        'constraint': '',
        'callable': None,
        'params': None
    },
    'impulse': {
        'dtype': 'VARCHAR(5)',
        'constraint': '',
        'callable': None,
        'params': None
    }
}

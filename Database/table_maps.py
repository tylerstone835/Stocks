from polygon_api import *


daily_table_map = {
    'date': {
        'dtype': 'DATE',
        'constraint': 'NOT NULL',
        'primary_key': True,
        'callable': None,
        'params': None
    },
    'symbol': {
        'dtype': 'VARCHAR(10)',
        'constraint': 'NOT NULL',
        'primary_key': True,
        'callable': None,
        'params': None
    },
    'open': {
        'dtype': 'NUMBER(20, 3)',
        'constraint': 'NOT NULL',
        'primary_key': False,
        'callable': get_price_action,
        'params': {'multiplier': 1, 'timespan': 'day'}
    },
    'high': {
        'dtype': 'NUMBER(20, 3)',
        'constraint': 'NOT NULL',
        'primary_key': False,
        'callable': None,
        'params': None
    },
    'low': {
        'dtype': 'NUMBER(20, 3)',
        'constraint': 'NOT NULL',
        'primary_key': False,
        'callable': None,
        'params': None
    },
    'close': {
        'dtype': 'NUMBER(20, 3)',
        'constraint': 'NOT NULL',
        'primary_key': False,
        'callable': None,
        'params': None
    },
    'volume': {
        'dtype': 'NUMBER(20, 3)',
        'constraint': 'NOT NULL',
        'primary_key': False,
        'callable': None,
        'params': None
    },
    'sma_50': {
        'dtype': 'NUMBER(20, 3)',
        'constraint': '',
        'primary_key': False,
        'callable': get_sma,
        'params': {'timespan': 'day', 'window': 50}
    },
    'ema_5': {
        'dtype': 'NUMBER(20, 3)',
        'constraint': '',
        'primary_key': False,
        'callable': get_ema,
        'params': {'timespan': 'day', 'window': 5}
    },
    'ema_10': {
        'dtype': 'NUMBER(20, 3)',
        'constraint': '',
        'primary_key': False,
        'callable': get_ema,
        'params': {'timespan': 'day', 'window': 10}
    },
    'ema_20': {
        'dtype': 'NUMBER(20, 3)',
        'constraint': '',
        'primary_key': False,
        'callable': get_ema,
        'params': {'timespan': 'day', 'window': 20}
    },
    'macd_histogram': {
        'dtype': 'NUMBER(20, 7)',
        'constraint': '',
        'primary_key': False,
        'callable': get_macd,
        'params': {'timespan': 'day'}
    },
    'deviation': {
        'dtype': 'NUMBER(20, 4)',
        'constraint': '',
        'primary_key': False,
        'callable': None,
        'params': None
    },
    'upper_channel': {
        'dtype': 'NUMBER(20, 2)',
        'constraint': '',
        'primary_key': False,
        'callable': None,
        'params': None
    },
    'lower_channel': {
        'dtype': 'NUMBER(20, 2)',
        'constraint': '',
        'primary_key': False,
        'callable': None,
        'params': None
    },
    'atr': {
        'dtype': 'NUMBER(20, 2)',
        'constraint': '',
        'primary_key': False,
        'callable': None,
        'params': None
    },
    'impulse': {
        'dtype': 'VARCHAR(5)',
        'constraint': '',
        'primary_key': False,
        'callable': None,
        'params': None
    }
}

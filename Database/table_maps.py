daily_table_map = {
    'date': {
        'dtype': 'DATE',
        'constraint': 'PRIMARY KEY'
    },
    'symbol': {
        'dtype': 'VARCHAR(10)',
        'constraint': 'PRIMARY KEY'
    },
    'open': {
        'dtype': 'NUMBER(20, 3)',
        'constraint': 'NOT NULL'
    },
    'high': {
        'dtype': 'NUMBER(20, 3)',
        'constraint': 'NOT NULL'
    },
    'low': {
        'dtype': 'NUMBER(20, 3)',
        'constraint': 'NOT NULL'
    },
    'close': {
        'dtype': 'NUMBER(20, 3)',
        'constraint': 'NOT NULL'
    },
    'volume': {
        'dtype': 'NUMBER(20, 3)',
        'constraint': 'NOT NULL'
    },
    'sma_50': {
        'dtype': 'NUMBER(20, 3)',
        'constraint': ''
    },
    'ema_5': {
        'dtype': 'NUMBER(20, 3)',
        'constraint': ''
    },
    'ema_10': {
        'dtype': 'NUMBER(20, 3)',
        'constraint': ''
    },
    'ema_20': {
        'dtype': 'NUMBER(20, 3)',
        'constraint': ''
    },
    'macd_histogram': {
        'dtype': 'NUMBER(20, 7)',
        'constraint': ''
    },
    'deviation': {
        'dtype': 'NUMBER(20, 4)',
        'constraint': ''
    },
    'upper_channel': {
        'dtype': 'NUMBER(20, 2)',
        'constraint': ''
    },
    'lower_channel': {
        'dtype': 'NUMBER(20, 2)',
        'constraint': ''
    },
    'atr': {
        'dtype': 'NUMBER(20, 2)',
        'constraint': ''
    },
    'impulse': {
        'dtype': 'VARCHAR(5)',
        'constraint': ''
    }
}

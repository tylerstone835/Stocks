daily_map = {
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
    'fast_line': {
        'dtype': 'NUMBER(20, 7)',
        'constraint': ''
    },
    'signal_line': {
        'dtype': 'NUMBER(20, 7)',
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


weekly_map = {
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
    'fast_line': {
        'dtype': 'NUMBER(20, 7)',
        'constraint': ''
    },
    'signal_line': {
        'dtype': 'NUMBER(20, 7)',
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


monthly_map = {
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
    'fast_line': {
        'dtype': 'NUMBER(20, 7)',
        'constraint': ''
    },
    'signal_line': {
        'dtype': 'NUMBER(20, 7)',
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


overview_map = {
    'list_date': {
        'dtype': 'DATE',
        'constraint': ''
    },
    'symbol': {
        'dtype': 'VARCHAR(10)',
        'constraint': 'PRIMARY KEY'
    },
    'name': {
        'dtype': 'VARCHAR(100)',
        'constraint': ''
    },
    'description': {
        'dtype': 'VARCHAR(1000)',
        'constraint': ''
    },
    'sic_code': {
        'dtype': 'NUMBER(10, 0)',
        'constraint': ''
    },
    'sic_description': {
        'dtype': 'VARCHAR(100)',
        'constraint': ''
    },
    'market_cap': {
        'dtype': 'NUMBER(20, 3)',
        'constraint': ''
    },
    'outstanding_shares': {
        'dtype': 'NUMBER(20, 0)',
        'constraint': ''
    },
    'round_lot': {
        'dtype': 'NUMBER(10, 0)',
        'constraint': ''
    },
    'total_employees': {
        'dtype': 'NUMBER(10, 0)',
        'constraint': ''
    },
    'homepage_url': {
        'dtype': 'VARCHAR(100)',
        'constraint': ''
    },
    'logo_url': {
        'dtype': 'VARCHAR(1000)',
        'constraint': ''
    }
}


date_dimension_map = {
    'date': {
        'dtype': 'DATE',
        'constraint': 'PRIMARY KEY'
    },
    'description': {
        'dtype': 'VARCHAR(20)',
        'constraint': 'NOT NULL'
    },
    'day': {
        'dtype': 'VARCHAR(10)',
        'constraint': 'NOT NULL'
    },
    'day_of_week': {
        'dtype': 'NUMBER(1, 0)',
        'constraint': 'NOT NULL'
    },
    'day_of_month': {
        'dtype': 'NUMBER(2, 0)',
        'constraint': 'NOT NULL'
    },
    'day_of_year': {
        'dtype': 'NUMBER(3, 0)',
        'constraint': 'NOT NULL'
    },
    'week_number': {
        'dtype': 'NUMBER(2, 0)',
        'constraint': 'NOT NULL'
    },
    'month': {
        'dtype': 'VARCHAR(10)',
        'constraint': 'NOT NULL'
    },
    'month_number': {
        'dtype': 'NUMBER(2, 0)',
        'constraint': 'NOT NULL'
    },
    'is_month_start': {
        'dtype': 'BOOLEAN',
        'constraint': 'NOT NULL'
    },
    'is_month_end': {
        'dtype': 'BOOLEAN',
        'constraint': 'NOT NULL'
    },
    'year': {
        'dtype': 'NUMBER(4, 0)',
        'constraint': 'NOT NULL'
    },
    'is_year_start': {
        'dtype': 'BOOLEAN',
        'constraint': 'NOT NULL'
    },
    'is_year_end': {
        'dtype': 'BOOLEAN',
        'constraint': 'NOT NULL'
    },
    'is_leap_year': {
        'dtype': 'BOOLEAN',
        'constraint': 'NOT NULL'
    },
    'is_holiday': {
        'dtype': 'BOOLEAN',
        'constraint': 'NOT NULL'
    },
    'holiday': {
        'dtype': 'VARCHAR(100)',
        'constraint': ''
    },
    'is_market_holiday': {
        'dtype': 'BOOLEAN',
        'constraint': 'NOT NULL'
    },
    'market_holiday': {
        'dtype': 'VARCHAR(100)',
        'constraint': ''
    }
}

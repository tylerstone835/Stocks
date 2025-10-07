from procedures import *
from datetime import datetime

def main():

    # ___________ update daily table ___________
    update_daily_price_action()
    update_sma(window=50, table='daily')
    update_ema(window=5, table='daily')
    update_ema(window=10, table='daily')
    update_ema(window=20, table='daily')
    update_macd(table='daily')
    update_keltner(table='daily')
    update_atr(table='daily')
    update_impulse(table='daily')

    # ___________ update weekly table ___________
    update_weekly_price_action()
    update_ema(window=5, table='weekly')
    update_ema(window=10, table='weekly')
    update_ema(window=20, table='weekly')
    update_macd(table='weekly')
    update_keltner(table='weekly', channel_window=26)
    update_atr(table='weekly')
    update_impulse(table='weekly')


if __name__ == '__main__':
    main()

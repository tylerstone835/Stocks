from procedures import *


def main():
    update_daily_price_action()
    update_sma(window=50, table='daily')
    update_ema(window=5, table='daily')
    update_ema(window=10, table='daily')
    update_ema(window=20, table='daily')

    update_weekly_price_action()
    update_ema(window=5, table='weekly')
    update_ema(window=10, table='weekly')
    update_ema(window=20, table='weekly')


if __name__ == '__main__':
    main()

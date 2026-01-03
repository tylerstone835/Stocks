from symbol import Symbol


def channel_resumption(
    symbol: Symbol,
) -> None:

    for period in symbol:

        """
        Level One: Penetrate the channel with a 6-month macd record
        with trend alignment. No demotion logic at bottom.
        """
        if (
            (symbol.current_macd == symbol.max_macd
            or symbol.current_macd == symbol.min_macd)
            and symbol.channel_status == 'Penetrated'
            and symbol.trend
            and symbol.logic_index == 0
        ):
            symbol.promote()
            continue

        """
        Level Two: Reach value and or cool impulse. If trend breaks, demote.
        """
        if symbol.logic_index == 1 and not symbol.trend:
            symbol.demote(symbol.logic_index)
        elif (
            symbol.logic_index == 1
            and symbol.value_status
            and symbol.impulse_status == 'Resuming'
        ):
            symbol.promote(2)
            continue

        elif (
            symbol.logic_index == 1
            and symbol.value_status
        ):
            symbol.promote()
            continue


        """
        Level Three: If it reached value, but hasn't cooled yet, wait to
        see if it cools or breaks the trend.
        """
        if symbol.logic_index == 2 and not symbol.trend:
            symbol.demote(symbol.logic_index)
        elif (
            symbol.logic_index == 2
            and symbol.impulse_status == 'Resuming'
        ):
            symbol.promote()
            continue

        """
        Level Four: All criteria met, wait for value retracement for trigger
        """
        if symbol.logic_index == 3 and not symbol.trend:
            symbol.demote(symbol.logic_index)
        elif (
            symbol.logic_index == 3
            and symbol.value_status
        ):
            symbol.promote()


        """
        Entry Trigger: Print stats and reset logic index.
        """
        if symbol.logic_index == 4:
            symbol.plot_data()
            symbol.demote(symbol.logic_index)

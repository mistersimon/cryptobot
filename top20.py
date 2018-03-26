"Defins a strategy that holds the top 20 coins on binance equally"
import os.path

import strategy
import exchange
import fund
import menu


def fund_def():
    """Fund defintion
    """

    # CSV filename containing holdings
    filename = 'top20.csv'

    num_coins = 20  # Number of coins to hold

    # Lets exclude some coins we don't want
    excluded_coins = ["USDT",  # Tether - No potential for profit
                      "XEM",   # NEM - Not on binance
                      "BCN"]   # Bytecoin - Not on binance

    top20_strategy = strategy.EqualTop(num_coins, excluded_coins)
    exchanges = {}
    exchanges['binance'] = exchange.Binance()
    top20 = fund.Fund(top20_strategy, exchanges)

    # Set filename
    top20.filename = filename

    # Load current holdings
    if os.path.exists(filename):
        top20.transactions_load()

    return top20


if __name__ == '__main__':
    FUND = fund_def()
    menu.enter_menu(FUND)

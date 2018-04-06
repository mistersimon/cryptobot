#!/usr/bin/env python3
"""
Uses cryptobot to manage a fund that holds the top 20 Coins on binance, with equal weighting.
"""


from cryptobot import strategy
from cryptobot import exchange
from cryptobot import fund
from cryptobot import menu


def fund_def():
    "Creates and returns a fund object with the top20 strategy on Binance"

    # CSV filename to store transactions
    fname_transactions = 'top20.csv'

    # Hold the top N number of coins
    num_coins = 20

    # Lets exclude some coins we don't want
    excluded_coins = ["USDT",  # Tether - No potential for profit
                      "XEM",   # NEM - Not on binance
                      "BCN"]   # Bytecoin - Not on binance

    # Create a strategy object for the this strategy
    top20_strategy = strategy.EqualTop(num_coins, excluded_coins)

    # Setup Exchanges
    exchanges = {}
    exchanges['binance'] = exchange.Binance()

    # Create Fund object
    top20 = fund.Fund(top20_strategy, exchanges, fname_transactions)

    return top20


if __name__ == '__main__':
    # Create fund and enter menu
    FUND = fund_def()
    menu.enter_menu(FUND)

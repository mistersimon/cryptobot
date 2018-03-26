"""Fund class

This class implements functionality to adminstrate a fund.

"""

import pandas as pd

# For trading
from binance.client import Client
# from binance.enums import *
import config


class Fund():
    """Initalisation

    Args:
      strategy (obj): A strategy class that defines the strategy of the portfolio
      fiat_base (str): Default reporting category for fiat
      crypto_base (str): Default reporting category for crypto

    Attributes:
      trades_pending (list): List of tuples containings trades to excute
      holdings (DataFrame): Table of coins and holding
      filename (str): Location of csv containing holdings

    """

    # pylint: disable=too-many-instance-attributes
    # 8 is a reasonable number of attributes

    def __init__(self, strategy, exchanges, fiat_base='USD', crypto_base='BTC'):

        self.strategy = strategy
        self.exchanges = exchanges
        self.fiat_base = fiat_base
        self.crypto_base = crypto_base
        self.trades_pending = {}
        self.transactions = pd.DataFrame()
        self.filename = None

        # Intialise binance client with api keys
        self.binance = Client(config.BINANCE_KEY,
                              config.BINANCE_SECRET)

    def nav(self):
        """Calculates the current worth of the portfolio"""

        # Get current holdings
        holdings = self.current_holdings()

        # Get list of trading pairs (removing base crypto)
        trading_pairs = list(holdings.keys())
        trading_pairs = [x for x in trading_pairs if x != self.crypto_base]

        # Lookup prices for trading pairs
        prices = self.exchanges['binance'].get_all_prices(trading_pairs)
        # print(prices)

        # Add back base crypto
        prices[self.crypto_base] = (1.0, 'Price')

        # Calculate holdings in base currency
        holdings_base = {sym: (amt * prices[sym][0], self.crypto_base)
                         for sym, (amt, _) in holdings.items()}

        # Calculate net asset value
        nav = sum([v for v, _ in holdings_base.values()])

        return (nav, holdings_base)

    def current_holdings(self):
        """Returns the current holdings based on transactions saved"""
        holdings = self.transactions.groupby('pair')['quote'].sum().to_dict()
        return {k: (v, k.split('/')[0]) for k, v in holdings.items()}

    def add_trades(self, trades):
        """ Adds list of trades to pending trades
        """
        for sym, _ in trades.items():
            if sym in self.trades_pending:
                if self.trades_pending[sym][1] != trades[sym][1]:
                    raise ValueError("Non matching curriencies in trade")
                self.trades_pending[sym] = (
                    self.trades_pending[sym][0] + trades[sym][0], trades[sym][1])
            else:
                self.trades_pending[sym] = trades[sym]

    def _get_target(self):
        """Calculates the target holding for the portfolio"""
        return {sym+'/'+self.crypto_base if sym != self.crypto_base else sym: (val, unit)
                for sym, (val, unit) in self.strategy.target_holding().items()}

    def rebalance(self):
        """Calculates the neccesary trades to bring the portfolio back to target"""

        holdings = self.current_holdings()

        (nav, holdings_base) = self.nav()

        # Calculate target portolfio in base/BTC currency
        target_base = {k: (v*nav, 'BTC')
                       for k, (v, _) in self._get_target().items()}

        # print(holdings)
        # print(holdings_base)
        # print(target_base)

        transactions = target_base.copy()

        for sym, (_, unit) in holdings_base.items():
            # Deduct what we have from target portfolio
            if sym in transactions:
                if unit == transactions[sym][1]:
                    transactions[sym] = (transactions[sym][0] -
                                         holdings_base[sym][0], unit)
                else:
                    raise ValueError('Incorrect Unit for rebalancing')
            # If we dont want this coin anymore, dump all of it.
            else:
                # Specify unit in quote currency to ensure we liquidate all!
                transactions[sym] = (-holdings[sym][0], holdings[sym][1])

        self.add_trades(transactions)

    def capital_add(self, amount):
        """Adds capital into fund according to exisiting strategy

        Note: This does not rebalance the fund
        """
        currency = 'BTC'
        target = self._get_target()
        trades = {sym: (v*amount, currency) for sym, (v, _) in target.items()}

        self.add_trades(trades)

    def get_pending_trades(self):
        """Returns the list of pending trades"""
        return self.trades_pending

    def excute_trades(self):
        """ Excute all pending trades
        """

        transactions_inserts = []

        # Loop over each order
        for trade in self.trades_pending.items():

            order = self.exchanges['binance'].prepare_order(trade)

            if order[0] == self.crypto_base:
                pass
            else:
                order = self.exchanges['binance'].excute_order(order)

            if order != {}:
                pair, (qty, price, side) = order
                price = float(price)
                qty = float(qty)

                if side == 'SELL':
                    qty *= -1

                transactions_inserts.append({
                    "pair": pair,
                    "price": price,
                    "quote": qty,
                    "base": price*qty,
                })

        # Add to transactions dataframe
        self.transactions = self.transactions.append(
            transactions_inserts, ignore_index=True)
        self.transactions_save()

    def transactions_save(self):
        """ Save transactions to csv
        """
        if self.filename is None:
            raise ValueError("No filename set for transactions file")

        self.transactions.to_csv(self.filename, index_label='id')

    def transactions_load(self):
        """ Load transactions from csv
        """
        if self.filename is None:
            raise ValueError("No filename set for holdings file")
        self.transactions = pd.read_csv(self.filename, index_col='id')

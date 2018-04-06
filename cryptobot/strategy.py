""" Strategy class

Implementation of a certain fund strategy. Needs to return a target holding at current time

"""
import pandas as pd


# pylint: disable=too-few-public-methods
# Using classes to ensure consistent api through different strategies

class Strategy():
    """
    Returns a list of the desired holdings of the startegy at the time of running. 
    """

    def target_holding(self):
        """ Returns list of tuples with target holdings for portfolio

         tuple format: (symbol, holding, '%')
         """
        raise NotImplementedError


class EqualTop(Strategy):
    """ Strategy equally holds the top N coins on CMC at any given time

    args:
      num_coins (int): number of top coins to take from CMC
      excluded_coins (list): List of symbols to exclude from CMC
    """

    def __init__(self, num_coins, excluded_coins=None):
        self.num_coins = num_coins
        self.excluded_coins = excluded_coins or []

        # Set weightage equal
        self.weightage = 1 / num_coins

    def target_holding(self):
        """ Returns dictionary target holdings for portfolio
        """

        # Grab tickers within search range
        search_range = self.num_coins + len(self.excluded_coins)
        url = 'https://api.coinmarketcap.com/v1/ticker/?limit={}'.format(
            search_range)
        tickers = pd.read_json(url)

        # Filter out ones we don't want
        tickers = tickers.loc[~tickers['symbol'].isin(self.excluded_coins)]

        # Take the number of coins we are instrested in
        tickers = tickers[:self.num_coins]

        # Get list of symbols
        symbols = tickers['symbol'].tolist()

        holdings = {k: (self.weightage, '%') for k in symbols}

        # Return only the holdings
        return holdings

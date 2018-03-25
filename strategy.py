""" Strategy class

Implementation of a certain fund strategy. Needs to return a target holding at current time

"""
import pandas as pd

class strategy():
  """ Base class
  """
  def targetHolding(self):
    """ Returns list of tuples with target holdings for portfolio 

    tuple format: (symbol, holding, '%')
    """
    pass


class equalTop(strategy):
  """ Strategy equally holds the top N coins on CMC at any given time
  
  args:
    numCoins (int): number of top coins to take from CMC
    excludedCoins (list): List of symbols to exclude from CMC
  """
  def __init__(self, numCoins, excludedCoins = []):
    self.numCoins = numCoins
    self.excludedCoins = excludedCoins

    # Set weightage equal
    self.weightage = 1 / numCoins
    

  def targetHolding(self):
    """ Returns dictionary target holdings for portfolio 
    """

    # Grab tickers within search range
    search_range = self.numCoins + len(self.excludedCoins)
    url = 'https://api.coinmarketcap.com/v1/ticker/?limit={}'.format(search_range)
    tickers = pd.read_json(url)

    # Filter out ones we don't want
    tickers = tickers.loc[~tickers['symbol'].isin(self.excludedCoins)]

    # Take the number of coins we are instrested in
    tickers = tickers[:self.numCoins]

    # Get list of symbols
    symbols = tickers['symbol'].tolist()

    holdings = { k:(self.weightage,'%') for k in symbols }

    # Return only the holdings
    return holdings 

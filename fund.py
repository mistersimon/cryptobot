"""Fund class

This class implements functionality to adminstrate a fund.

"""

import pandas as pd

# For trading
from binance.client import Client
from binance.enums import *
import config

import exchange

class fund():
  """Initalisation

  Args:
    strategy (obj): A strategy class that defines the strategy of the portfolio
    fiatBase (str): Default reporting category for fiat
    cryptoBase (str): Default reporting category for crypto
  
  Attributes:
    tradesPending (list): List of tuples containings trades to excute
    holdings (DataFrame): Table of coins and holding
    filename (str): Location of csv containing holdings
  
  """
  def __init__(self, strategy, exchanges, fiatBase = 'USD', cryptoBase = 'BTC'):
    
    self.strategy = strategy
    self.exchanges = exchanges
    self.fiatBase = fiatBase
    self.cryptoBase = cryptoBase
    self.tradesPending = {}
    self.transactions = pd.DataFrame()
    self.filename = None

    # Intialise binance client with api keys
    self.binance = Client(config.binance_api_key, config.binance_api_secret)


  def NAV(self):

    # Get current holdings
    holdings = self.current_holdings()
    
    # Get list of trading pairs (removing base crypto)
    tradingPairs = list(holdings.keys())
    tradingPairs = [x for x in tradingPairs if x != self.cryptoBase]

    # Lookup prices for trading pairs
    prices = self.exchanges['binance'].getAllPrices(tradingPairs)
    # print(prices)

    # Add back base crypto
    prices[self.cryptoBase] = (1.0, 'Price')

    # Calculate holdings in base currency
    holdings_base = {sym:(amt * prices[sym][0], self.cryptoBase) for sym,(amt,_) in holdings.items()}

    # Calculate net asset value
    NAV = sum([v for v,_ in holdings_base.values()])

    return (NAV, holdings_base)

  def current_holdings(self):
    holdings = self.transactions.groupby('pair')['quote'].sum().to_dict()
    return {k:(v, k.split('/')[0]) for k,v in holdings.items()} 

  def addTrades(self, trades):
    """ Adds list of trades to pending trades
    """
    for s,(v, u) in trades.items():
      if s in self.tradesPending:
        if self.tradesPending[s][1] != trades[s][1]:
          raise ValueError("Non matching curriencies in trade")
        self.tradesPending[s] = (self.tradesPending[s][0] + trades[s][0], trades[s][1])
      else:
        self.tradesPending[s] = trades[s]
  
  def _getTarget(self):
    return { sym+'/'+self.cryptoBase if sym != self.cryptoBase else sym: (val, unit) for sym, (val, unit) in self.strategy.targetHolding().items()}

  def rebalance(self):

    holdings = self.current_holdings()

    (NAV, holdings_base) = self.NAV()

    # Calculate target portolfio in base/BTC currency
    target_base = { k:(v*NAV,'BTC') for k,(v,_) in self._getTarget().items()}

    # print(holdings)
    # print(holdings_base)
    # print(target_base)

    transactions = target_base.copy()

    for sym, (amt, unit) in holdings_base.items():
      # Deduct what we have from target portfolio
      if sym in transactions:
        if unit == transactions[sym][1]:
          transactions[sym] = (transactions[sym][0]-holdings_base[sym][0], unit)
        else:
          raise ValueError('Incorrect Unit for rebalancing')
      # If we dont want this coin anymore, dump all of it.
      else:
        # Specify unit in quote currency to ensure we liquidate all!
        transactions[sym] = (-holdings[sym][0], holdings[sym][1])      

    self.addTrades(transactions)

  def capital_add(self, amount):
    """Adds capital into fund according to exisiting strategy

    Note: This does not rebalance the fund
    """
    currency = 'BTC'
    target = self._getTarget()
    trades = { sym:(v*amount, currency) for sym,(v,_) in target.items()}

    self.addTrades(trades)
  
  def getPendingTrades(self):
    return (self.tradesPending)

  def excuteTrades(self):
    """ Excute all pending trades
    """

    transsactionsInsert = []
    
    # Loop over each order
    for trade in self.tradesPending.items():

      order = self.exchanges['binance'].prepareOrder(trade)

      if order[0] == self.cryptoBase:
        pass
      else:
        order = self.exchanges['binance'].excuteOrder(order)

      if order != {}:
        pair, (qty, price, side) = order
        price = float(price)
        qty = float(qty)

        if side == 'SELL':
          qty *=  -1

        transsactionsInsert.append({
            "pair": pair,
            "price": price,
            "quote": qty,
            "base": price*qty,
        })
 
    #Add to transactions dataframe 
    self.transactions = self.transactions.append(transsactionsInsert, ignore_index=True)
    self.transactionsSave()

  def transactionsSave(self):
    """ Save transactions to csv
    """
    if self.filename == None:
      raise ValueError("No filename set for transactions file")

    self.transactions.to_csv(self.filename, index_label = 'id')

  def transactionsLoad(self, filename):
    """ Load transactions from csv
    """
    if self.filename == None:
      raise ValueError("No filename set for holdings file")
    self.transactions = pd.read_csv(self.filename, index_col = 'id')

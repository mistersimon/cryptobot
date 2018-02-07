"""Fund class

This class implements functionality to adminstrate a fund.

"""

import pandas as pd

# For trading
from binance.client import Client
from binance.enums import *
import config

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
  def __init__(self, strategy, fiatBase = 'USD', cryptoBase = 'BTC'):
    
    self.strategy = strategy
    self.fiatBase = fiatBase
    self.cryptoBase = cryptoBase
    self.tradesPending = []
    self.holdings = pd.DataFrame(columns=["holding"])
    self.filename = None

  def capital_add(self, amount):
    """Adds capital into fund according to exisiting strategy

    Note: This does not rebalance the fund
    """
    currency = 'BTC'
    target = self.strategy.targetHolding()
    trades = [ ("BUY",sym,v*amount,currency) for (sym,v,_) in target ]

    self.tradesPending += trades
  
  def getPendingTrades(self):
    return (self.tradesPending)

  def _filterOrder(self, binance, pair, qty, price):
    """Filter order according to BINANCE rules
    
    """
    newQty = qty

    # Get symbol info from binance
    info = binance.get_symbol_info(pair)


    # Process LOT Size Filters
    filter = next((item for item in info['filters'] if item["filterType"] == "LOT_SIZE"))
    minQty = float(filter['minQty'])
    stepSize = float(filter['stepSize'])

    # Ensure qty is more than minimum
    if qty < minQty:
      newQty = minQty 
    
    # Ensure qty is a multiple of stepsize
    if (qty - minQty) % stepSize != 0:
      newQty = stepSize * round(qty/stepSize)


    # Handle Notional Size Filters
    filter = next((item for item in info['filters'] if item["filterType"] == "MIN_NOTIONAL"))
    min = float(filter['minNotional'])
    
    # Increase qty by step size until notional size is reached
    while newQty*price < min:
      newQty += stepSize

    # Calculate change in quanty
    delta = round((newQty/qty-1)*100,2)

    return (newQty, delta)

  def excuteTrades(self):
    """ Excute all pending trades
    """

    # Intialise binance client with api keys
    client = Client(config.binance_api_key, config.binance_api_secret)

    
    # Loop over each order
    for (side, sym, qty, curr) in self.tradesPending:
      
      # Check trade has right curr
      if curr != self.cryptoBase:
        raise ValueError('Expecting trade in BTC value')

      # Binance has different names compared to CMC, rename
      binanceReMapping = {'BCH':'BCC','MIOTA':'IOTA', 'XRB':'NANO'}
      if sym in binanceReMapping:
        sym = binanceReMapping[sym]

      # Don't need to 'trade' BTC/Base currency
      if sym != self.cryptoBase:

        # Find trading pair
        pair = sym + self.cryptoBase

        # Get current price information
        ticker = client.get_ticker(symbol=pair)
        price = float(ticker['bidPrice'])

        # Calculate rough price then filter
        qty /= price
        (qty, delta) = self._filterOrder(client, pair, qty, price)

        #Convert floats to strings to send to binance
        qtyStr = "{:0.0{}f}".format(qty, 5)
        priceStr = "{:0.0{}f}".format(price, 8)

        # Get conformation
        resp = input('Buying {} of {}  for {}. Delta {}%. Approve (Y/n)?'.format(qtyStr, pair, priceStr, delta))
        
        # Send order to binance
        if resp == 'Y':
          #Simulate order with create_test_order
          order = client.create_order(
            symbol=pair,
            quantity=qtyStr,
            price=priceStr,
            side=SIDE_BUY,
            type=ORDER_TYPE_LIMIT,
            timeInForce=TIME_IN_FORCE_GTC)
        else:
          continue

      #Add to holdings table
      if sym in self.holdings.index:
        self.holdings.loc[sym] += qty
      else:
        self.holdings.loc[sym] = qty 
 
  def holdingSave(self):
    """ Save holdings to csv
    """
    if self.filename == None:
      raise ValueError("No filename set for holdings file")

    self.holdings.to_csv(self.filename, index_label = 'symbol')

  def holdingLoad(self, filename):
    """ Load holdings from csv
    """
    if self.filename == None:
      raise ValueError("No filename set for holdings file")
    self.holdings = pd.read_csv(self.filename, index_col = 'symbol')

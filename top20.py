import strategy
import fund
import menu

import os.path

def fundDef():
  """Fund defintion
  """

  # CSV filename containing holdings
  filename = 'top20.csv'

  numCoins = 20 # Number of coins to hold

  # Lets exclude some coins we don't want
  excludedCoins = ["USDT",  # Tether - No potential for profit
                    "XEM",   # NEM - Not on binance
                    "BCN"]   # Bytecoin - Not on binance

  top20 = fund.fund(strategy.equalTop(numCoins, excludedCoins))

  #Set filename
  top20.filename = filename

  # Load current holdings
  if os.path.exists(filename):
    top20.holdingLoad(filename)

  return top20

if __name__ == '__main__':
  fund = fundDef()
  menu.menu(fund)


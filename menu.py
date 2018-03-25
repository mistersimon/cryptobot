""" Simple CLI menu driven interface for fund class
"""

def menu(fund):
  #Dictionary of tuples with prompt and handler
  menu = {}

  """ Exit """
  def exitHandler():
    fund.transactionsSave()
    exit()
  menu['q'] = ("Exit", exitHandler)

  """ View Current Holdings """
  def currentHoldings():
    print("Current Holdings: ", fund.current_holdings())
    (NAV, holdings) = fund.NAV()
    print("Current Holdings (in BTC): " ,holdings)
    print("Current portfolio value (in BTC): " , NAV)

  menu['1'] = ("View current holding", currentHoldings)

  """ View Pending Trades Capital """
  def printPendingTrades():
    # print("Pending trades:\n   ", '\n    '.join(map(str,fund.getPendingTrades())))
    trades = fund.getPendingTrades() 
    print(trades)
    print('Number of trades pending: {}'.format(len(trades)))

  menu['2'] = ("View pending trades", printPendingTrades)

  """ Add Capital """
  def addFunds():
    amount = float(input("How much do you want to invest? (BTC): "))
    fund.capital_add(amount)
    print('Invested {} in pending trades.'.format(amount))

  menu['3'] = ("Add Funds", addFunds)

  """ Rebalance Portfolio """
  def rebalance():
    fund.rebalance()
    print('Fund Rebalanced')

  menu['4'] = ("Rebalance portfolio", rebalance)

  """ Excute pending Trades """
  def excuteTrades():
    print("Trades to be excuted:")
    printPendingTrades()
    excute = input("Proceed with excuction? (Y/n)")
    if excute == "Y":
      fund.excuteTrades()
    else:
      "Excutation cancel"

  menu['5'] = ("Excute pending trades", excuteTrades)


  """ Clear pending Trades """
  def clearTrades():
    print("Trades cleared")
    fund.tradesPending = {}

  menu['6'] = ("Clear pending trades", clearTrades)


  while True:
    # Clear screen
    print(chr(27) + "[2J")

    # Print all options
    for entry in sorted(menu.keys()):
      print(entry, menu[entry][0])
    
    selection = input("Please select option: ")

    # Run menu handler
    menu[selection][1]()

    input("Press any key to return to menu")
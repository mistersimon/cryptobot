""" Simple CLI menu driven interface for fund class
"""

def menu(fund):
  #Dictionary of tuples with prompt and handler
  menu = {}

  """ Exit """
  def exitHandler():
    fund.holdingSave()
    exit()
  menu['q'] = ("Exit", exitHandler)

  """ View Current Holdings """
  def currentHoldings():
    print(fund.holdings)

  menu['1'] = ("View current holding", currentHoldings)

  """ View Pending Trades Capital """
  def printPendingTrades():
    print("Pending trades:\n   ", '\n    '.join(map(str,fund.getPendingTrades())))

  menu['2'] = ("View pending trades", printPendingTrades)

  """ Add Capital """
  def addFunds():
    amount = float(input("How much do you want to invest? (BTC): "))
    fund.capital_add(amount)
    print('Invested {} in pending trades.'.format(amount))

  menu['3'] = ("Add Funds", addFunds)

  """ Excute pending Trades """
  def excuteTrades():
    print("Trades to be excuted:")
    printPendingTrades()
    excute = input("Proceed with excuction? (Y/n)")
    if excute == "Y":
      fund.excuteTrades()
    else:
      "Excutation cancel"

  menu['4'] = ("Excute pending trades", excuteTrades)


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
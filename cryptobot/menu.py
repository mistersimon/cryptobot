"""Simple CLI menu driven interface for fund class
"""


def enter_menu(fund):
    """Runs a simple text driven menu"""
    # Dictionary of tuples with prompt and handler
    menu = {}

    def exit_handler():
        """ Exit """
        fund.transactions_save()
        exit()

    def current_holdings():
        """ View Current Holdings """
        print("Current Holdings: ", fund.current_holdings())
        (nav, holdings) = fund.nav()
        print("Current Holdings (in BTC): ", holdings)
        print("Current portfolio value (in BTC): ", nav)

    def pending_trades():
        """ View Pending Trades Capital """
        # print("Pending trades:\n   ", '\n    '.join(map(str,fund.getPendingTrades())))
        trades = fund.get_pending_trades()
        print(trades)
        print('Number of trades pending: {}'.format(len(trades)))

    def add_funds():
        """ Add Capital """
        amount = float(input("How much do you want to invest? (BTC): "))
        fund.capital_add(amount)
        print('Invested {} in pending trades.'.format(amount))

    def rebalance():
        """ Rebalance Portfolio """
        fund.rebalance()
        print('Fund Rebalanced')

    def excute_trade():
        """ Excute pending Trades """
        print("Trades to be excuted:")
        pending_trades()
        excute = input("Proceed with excuction? (Y/n)")
        if excute == "Y":
            fund.excute_trades()
        else:
            print("Excutation cancel")

    def clear_trade():
        """ Clear pending Trades """
        print("Trades cleared")
        fund.trades_pending = {}

    menu['1'] = ("View current holding", current_holdings)
    menu['2'] = ("View pending trades", pending_trades)
    menu['3'] = ("Add Funds", add_funds)
    menu['4'] = ("Rebalance portfolio", rebalance)
    menu['5'] = ("Excute pending trades", excute_trade)
    menu['6'] = ("Clear pending trades", clear_trade)
    menu['q'] = ("Exit", exit_handler)

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

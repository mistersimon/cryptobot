""" Class that handles all interactions with various exchanges"""
from functools import singledispatch

# For trading
from binance.client import Client
from binance.enums import SIDE_BUY, SIDE_SELL, ORDER_TYPE_LIMIT, TIME_IN_FORCE_GTC

import config


# Disable warning about mapper not being implemented as its a single-dispatch method
# pylint: disable=W0223

class Exchange():
    """Base class for exchanges, describing api"""

    # pylint: disable=E0213, E1101
    # Pylint doesn't like the singledispatch decorator

    def __init__(self):
        self.mapping = {}
        self.unmapping = {}

    @singledispatch
    def mapper(pair, mapping):
        """Overloaded function to swap symbol pairs"""
        raise NotImplementedError('Unsupported type')

    @mapper.register(str)
    def _(pair, mapping):
        """ Converts symbols on string input"""
        pair = pair.split('/')
        for i, sym in enumerate(pair):
            if sym in mapping:
                #                 print('Changing {} to {}'.format(pair[i], self.remapping[sym]))
                pair[i] = mapping[sym]
        return '/'.join(pair)

    @mapper.register(list)
    def _(pairs, mapping):
        """ Converts symbols on list input"""
        return [Exchange.mapper(x, mapping) for x in pairs]

    @mapper.register(dict)
    def _(pairs, mapping):
        """ Converts symbols on dict input"""
        return {Exchange.mapper(s, mapping): t for s, t in pairs.items()}

    @mapper.register(tuple)
    def _(pair, mapping):
        """ Converts symbols on tuple input"""
        return (Exchange.mapper(pair[0], mapping), pair[1])

    @staticmethod
    def remap_deco(func):
        """Decorator function to rename symbols if required"""

        def wrapper(self, pair):
            """Wrapper"""
            # Covert input from User to Exchange symbols
            inp = Exchange.mapper(pair, self.mapping)

            out = func(self, inp)

            # Convert output from Exchange to user symbols
            out = Exchange.mapper(out, self.unmapping)

            return out
        return wrapper

    def get_price(self, pair):
        """ Returns price for a single pair
        """
        pass

    def get_all_prices(self, pairs):
        """ Returns dictionary of all prices for a list of inputs
        """
        pass


class Binance(Exchange):
    """Class for binance exchange"""

    def __init__(self):
        super().__init__()
        self.client = Client(config.BINANCE_KEY, config.BINANCE_SECRET)
        self.mapping = {'BCH': 'BCC', 'MIOTA': 'IOTA'}
        self.unmapping = {v: k for k, v in self.mapping.items()}
        self.crypto_base = 'BTC'

    @Exchange.remap_deco
    def get_price(self, pair):
        pass

    @Exchange.remap_deco
    def get_all_prices(self, pairs):
        """Returns all the prices on binance exchange"""
        prices = {}
        exchange_prices = self.client.get_all_tickers()

        # Scrub Exchange prices
        exchange_prices = {x['symbol']: x['price'] for x in exchange_prices}

        for pair in pairs:

            prices[pair] = (
                float(exchange_prices[pair.replace("/", "")]), 'Price')
        return prices

    @Exchange.remap_deco
    def prepare_order(self, trade):
        """Prepares an order that compiles with binance exchange"""
        pair, (amt, unit) = trade
        if pair.find('/') != -1:
            [quote, base] = pair.split('/')
        else:
            quote = pair
            base = pair

        def order_side(amt):
            """Determine side for order"""
            if amt < 0:
                return (-amt, SIDE_SELL)
            elif amt > 0:
                return (amt, SIDE_BUY)
            else:
                raise ValueError("Invalid amount of trade")

        amt, side = order_side(amt)

        def determine_price(pair, side):
            """Get current spread on price"""
            if pair.find('/') == -1:
                if pair == self.crypto_base:
                    price = 1
                else:
                    raise ValueError("Incorrect pair")
            else:
                ticker = self.client.get_ticker(symbol=pair.replace('/', ''))
                if side == SIDE_BUY:
                    price = float(ticker['bidPrice'])
                elif side == SIDE_SELL:
                    price = float(ticker['askPrice'])
                else:
                    raise ValueError("Incorrect side input")

            return price

        price = determine_price(pair, side)

        # Calculate quantity for order
        if unit == quote:
            qty = amt
        elif base == self.crypto_base:
            qty = amt/price
        else:
            raise ValueError(
                'I do not know how to trade {} for {}'.format(pair, unit))

        # Return order
        order = (pair, (qty, price, side))
        return order

    def _filter_order(self, order):
        """Filter order according to BINANCE rules

        """
        pair, (qty, price, side) = order

        old_qty = qty

        # Get symbol info from binance
        info = self.client.get_symbol_info(pair.replace('/', ''))

        # Process LOT Size Filters
        criteria = next(
            (item for item in info['filters'] if item["filterType"] == "LOT_SIZE"))

        min_qty = float(criteria['minQty'])
        step_size = float(criteria['stepSize'])

        # Ensure qty is more than minimum
        if qty < min_qty:
            qty = min_qty

        # Ensure qty is a multiple of stepsize
        if (qty - min_qty) % step_size != 0:
            qty = step_size * round(qty/step_size)

        # Handle Notional Size Filters
        criteria = next(
            (item for item in info['filters'] if item["filterType"] == "MIN_NOTIONAL"))

        min_vol = float(criteria['minNotional'])

        # Increase qty by step size until notional size is reached
        while qty*price < min_vol:
            qty += step_size

        # Calculate change in quanty
        delta = round((qty/old_qty-1)*100, 2)

        # Convert floats to strings (for binance api)
        qty = '{:0.0{}f}'.format(qty, 5)
        price = '{:0.0{}f}'.format(price, 8)

        new_order = (pair, (qty, price, side))
        return (new_order, delta)

    @Exchange.remap_deco
    def excute_order(self, order, prompt=True):
        """Sends an order to the exchange, records on transaction list"""
        # TODO:- Check if order is actually clears

        # Change order to comply with binance filters
        (order, delta) = self._filter_order(order)

        # Unpack
        pair, (qty, price, side) = order

        # Get conformation (if required)
        if prompt:
            resp = input(
                '{} {} of {}  for {}. Delta {}%. Approve (Y/n)?'
                .format(side, qty, pair, price, delta))
        else:
            resp = None

        # Send order to exchange
        if prompt is False or resp == 'Y':
            # Simulate order with create_test_order
            self.client.create_test_order(
                symbol=pair.replace('/', ''),
                quantity=qty,
                price=price,
                side=side,
                type=ORDER_TYPE_LIMIT,
                timeInForce=TIME_IN_FORCE_GTC
            )
        else:
            order = {}

        return order

from functools import singledispatch

# For trading
from binance.client import Client
from binance.enums import *
import config


class exchange():
    def __init__(self):
        self.mapping = {}
        self.unmapping = {}
        pass

    
    @singledispatch
    @classmethod    
    def mapper(pair, mapping):
        raise NotImplementedError('Unsupported type')

    @mapper.register(str)
    def _(pair, mapping):
        """ Converts symbols based on mapping dictionary
        """
        pair = pair.split('/')
        for i, sym in enumerate(pair):
            if sym in mapping:
    #                 print('Changing {} to {}'.format(pair[i], self.remapping[sym]))
                pair[i] = mapping[sym]
        return ('/'.join(pair))

    @mapper.register(list)
    def _(pairs, mapping):
        return [ exchange.mapper(x, mapping) for x in pairs ]

    @mapper.register(dict)
    def _(pairs, mapping):
        return { exchange.mapper(s, mapping):t for s,t in pairs.items()}

    @mapper.register(tuple)
    def _(pair, mapping):
        return ( exchange.mapper(pair[0], mapping), pair[1] )
    
    def remapDeco(func):
        def wrapper(self, pair):
            # Covert input from User to exchange symbols
            inp = exchange.mapper(pair, self.mapping)
            
            out = func(self,inp)
            
            # Convert output from exchange to user symbols
            out = exchange.mapper(out, self.unmapping)
            
            return out
        return wrapper
    
    def getPrice(self, pair): 
        """ Returns price for a single pair
        """
        pass

    def getAllPrices(self, pairs):
        """ Returns dictionary of all prices for a list of inputs
        """
        pass

class binance(exchange):
    def __init__(self):
        self.client = Client(config.binance_api_key, config.binance_api_secret)
        self.mapping = {'BCH':'BCC','MIOTA':'IOTA'}
        self.unmapping = { v:k for k,v in self.mapping.items()}
        self.cryptoBase = 'BTC'

    @exchange.remapDeco
    def getPrice(self, pair):
        pass
    
    @exchange.remapDeco
    def getAllPrices(self, pairs): 
        prices = {}
        exchangePrices = self.client.get_all_tickers()
        # Scrub exchange prices
        exchangePrices = { x['symbol']:x['price'] for x in exchangePrices }

        for pair in pairs:
            
            prices[pair] = (float(exchangePrices[pair.replace("/","")]), 'Price')
        return prices
    
    
    @exchange.remapDeco
    def prepareOrder(self, trade):
        pair, (amt, unit) = trade
        if pair.find('/') != -1:
            [quote, base] = pair.split('/')
        else:
            quote = pair
            base = pair

        # Determine side for order
        if amt < 0:
            side = SIDE_SELL
            amt = -amt
        elif amt > 0:
            side = SIDE_BUY
        else:
            return None

        # Get current spread on price
        if quote == self.cryptoBase:
            price = 1
        else:
            ticker = self.client.get_ticker(symbol=pair.replace('/',''))
            if side == SIDE_BUY:
                price = float(ticker['bidPrice'])
            elif side == SIDE_SELL:
                price = float(ticker['askPrice'])
            else:
                #Code should never reach here. See above if block
                return None 
        
        # Calculate quantity for order
        if unit == quote:
            qty = amt
        elif base == self.cryptoBase:
            qty = amt/price
        else:
            raise ValueError('I do not know how to trade {} for {}'.format(pair, unit))

        # Return order
        order = (pair,(qty, price, side))
        return order

    def _filterOrder(self, order):
        """Filter order according to BINANCE rules
        
        """
        pair, (qty, price, side) = order

        oldQty = qty

        # Get symbol info from binance
        info = self.client.get_symbol_info(pair.replace('/',''))

        # Process LOT Size Filters
        filter = next((item for item in info['filters'] if item["filterType"] == "LOT_SIZE"))
        minQty = float(filter['minQty'])
        stepSize = float(filter['stepSize'])

        # Ensure qty is more than minimum
        if qty < minQty:
                qty = minQty 
            
        # Ensure qty is a multiple of stepsize
        if (qty - minQty) % stepSize != 0:
            qty = stepSize * round(qty/stepSize)


        # Handle Notional Size Filters
        filter = next((item for item in info['filters'] if item["filterType"] == "MIN_NOTIONAL"))
        min = float(filter['minNotional'])
        
        # Increase qty by step size until notional size is reached
        while qty*price < min:
            qty += stepSize

        # Calculate change in quanty
        delta = round((qty/oldQty-1)*100,2)

        #Convert floats to strings (for binance api)
        qtyStr = '{:0.0{}f}'.format(qty, 5)
        priceStr = '{:0.0{}f}'.format(price, 8)

        newOrder = (pair, (qtyStr, priceStr, side))
        return (newOrder, delta)

    
    @exchange.remapDeco
    def excuteOrder(self, order, prompt=True):

        # Change order to comply with binance filters
        (order, delta) = self._filterOrder(order)

        # Unpack
        pair, (qty, price, side) = order

        # Get conformation (if required)
        if prompt:
            resp = input('{} {} of {}  for {}. Delta {}%. Approve (Y/n)?'.format(side, qty, pair, price, delta))
        else:
            resp = None
      
        # Send order to exchange
        if prompt == False or resp == 'Y':
            #Simulate order with create_test_order
            self.client.create_test_order(
                symbol=pair.replace('/',''),
                quantity=qty,
                price=price,
                side=side,
                type=ORDER_TYPE_LIMIT,
                timeInForce=TIME_IN_FORCE_GTC
            )
        else:
            order = {}
         
        return order

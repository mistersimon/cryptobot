"""
Checks time difference between local time and binance server time

code from: https://github.com/sammchardy/python-binance/issues/2

"""

import time

from binance.client import Client
import config

CLIENT = Client(config.BINANCE_KEY, config.BINANCE_SECRET)

for i in range(1, 10):

    local_time1 = int(time.time() * 1000)

    server_time = CLIENT.get_server_time()

    diff1 = server_time['serverTime'] - local_time1

    local_time2 = int(time.time() * 1000)

    diff2 = local_time2 - server_time['serverTime']

    print("local1: %s server:%s local2: %s diff1:%s diff2:%s" %
          (local_time1, server_time['serverTime'], local_time2, diff1, diff2))

    time.sleep(2)

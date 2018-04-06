# Cryptobot

A set of python modules to roll out your own cryptofund. Define a target strategy and let cryptobot excute the trades for you!

This was built to avoid the management fees of 2+% the current funds are asking to adminstrate a fund for you.

Use this package at your own risk.

## Quick Start

The easiest way to get up and running is using on the example funds. Top20 buys the top 20 coins on Binance equally (with some expections).

1. First install the prerequisites with pipenv. Read how to install pipenv [here](https://docs.pipenv.org/#install-pipenv-today)

```shell
pipenv install
```

1. [Create a binance api key](https://www.binance.com/userCenter/createApi.html), and copy the details by coping sample_config.py to config.py and putting in your personal access keys/secerts

1. Enter the pipenv enviroment and run the top20 fund with the interactive menu

```shell
pipenv shell
python top20.py
```

## Features

* Calculate the current worth of the fund
* Add capital into the fund
* Rebalance the fund

## Status

The fund currently only supports the exchange Binance, and there is no mechanism to sell

## Built With

* [python-binance](https://github.com/sammchardy/python-binance) - Python wrapper for binance api

## Contributing

Feel free to implement other funds/Exchanges

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

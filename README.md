# Cryptobot

A set of python scripts to manage a cryptofund. Currently only implements binance api, and hence only coins on binance.

## Status

Current the fund can only add capital through the binance api. 

### Todo

* Impliment reblance
* Implement selling

## Getting Started

These instructions will get you a copy of the project up and running on your local machine.

### Prerequisites

The script relies on a few python modules, install them with:

```
pip install python-binance, pandas
```

### API Configuration

Add the API key and secrets to a config.py, following the format laid out in sample-config.py

### Running

The fund I personally use is defined in top20.py. To run it with the simple CLI interface:

```
python top20.py
```

Feel free to implement other funds

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

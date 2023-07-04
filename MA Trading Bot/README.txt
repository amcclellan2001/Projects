This program is in development and should not be trusted to trade (use paper trading, enabled by default).

This program is a moving average trading bot that uses the Alpaca API and Yahoo Finance data.
It compares the 15-minute and 60-minute moving averages and will buy on command if the 15-minute is above the 60-minute.
If the 15-minute crosses below the 60-minute, it will sell the position.

You will need the following:
-Alpaca Markets account
-IDE or TextEditor to input Alpaca API tokens into Python file
-Python 3.11
-Packages:
	-alpaca-py
	-yfinance
	-pandas
	-asyncio
-Ran in a Python environment.

Feel free to fork and push updates with credit.

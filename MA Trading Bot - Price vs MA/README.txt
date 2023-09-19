This program is a proof of concept and should not be trusted to trade (use paper trading, enabled by default).

This program is a moving average (MA) trading bot that uses the Alpaca API and Yahoo Finance data.
It compares the two user specified timeframes, the shorter coming first. 
If the shorter timeframe MA is above the longer timeframe MA, it will hold onto the position.
If the shorter timeframe MA is below the longer timeframe MA, it will close all positions.

You will need the following:
-Alpaca Trading account
-IDE or TextEditor to input Alpaca API tokens into Python file
-Python 3.11
-Packages:
	-alpaca-py
	-yfinance
	-pandas
	-asyncio
-Ran in a Python environment.

Known Bugs:
-Moving average input only works with daily timeframes
-Moving averages show up with NaN (not a real number)
-Bot closes all positions instead of the specified position

Feel free to fork and push updates with credit.
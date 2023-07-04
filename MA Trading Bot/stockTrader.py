# By Alex McClellan with Alpaca and Yahoo Finance

# Libraries
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
import time
import datetime
import yfinance as yf
import pandas as pd
import asyncio

# Get Historical Price Data
def get_historical_price_data(symbol, start_date, end_date, interval):
    ticker_data = yf.download(symbol, start=start_date, end=end_date, interval=interval)
    return ticker_data

# Calculate Moving Averages
def calculate_moving_averages(data, ma_period, ma_period2):
    data['ma_15'] = data["Close"].rolling(ma_period).mean()
    data['ma_60'] = data["Close"].rolling(ma_period2).mean()
    return data

# Trading Bot
async def run_algorithmic_trading_bot(trading_client, buying_power):
    # Enter ticker
    print("Enter the symbol of the asset you want to trade:")
    print("Example: ETH-USD, AAPL, F")
    symbol = input()

    # Moving average periods
    ma_period = "900T"  # 15-minute intervals
    ma_period2 = "3600T"  # 60-minute intervals

    yahoo_symbol = symbol.replace("-", "/")
    alpaca_symbol = symbol.replace("-", "")

    # Calculate the start date
    start_date = datetime.datetime.now() - datetime.timedelta(days=1)
    end_date = datetime.datetime.now()

    # Get historical price data
    ticker_data_15m = get_historical_price_data(symbol, start_date, end_date, "15m")
    ticker_data_60m = get_historical_price_data(symbol, start_date, end_date, "60m")

    # Check if the DataFrames are empty
    if ticker_data_15m.empty or ticker_data_60m.empty:
        print(f"No valid data available for ticker '{symbol}'.")
        return

    # Calculate the moving averages
    ticker_data_15m = calculate_moving_averages(ticker_data_15m, ma_period, ma_period2)
    ticker_data_60m = calculate_moving_averages(ticker_data_60m, ma_period, ma_period2)

    # Get the latest moving average values
    ma_15 = ticker_data_15m['ma_15'].iloc[-1]
    ma_60 = ticker_data_60m['ma_60'].iloc[-1]

    # Print the moving averages
    print(f"15-minute moving average for {symbol}: {ma_15:.4f}")
    print(f"60-minute moving average for {symbol}: {ma_60:.4f}")

    # Confirmation
    print(f"Would you like to buy {symbol}?")
    print(f"Type yes, no, or continue:")
    confirmation = input()

    # Check if a buy signal is generated
    if buying_power > 0 and confirmation.lower() == "yes" and ma_15 > ma_60:
        # Calculate the quantity based on the current price
        current_price = ticker_data_15m['Close'].iloc[-1]
        quantity = buying_power / current_price

        # Place the buy order
        market_order_data = MarketOrderRequest(
            symbol=alpaca_symbol,
            qty=buying_power,
            side=OrderSide.BUY,
            time_in_force=TimeInForce.GTC
        )
        market_order = trading_client.submit_order(order_data=market_order_data)
        print(f"Buy order placed: Buying {quantity} shares of {alpaca_symbol}.")

    elif confirmation.lower() == "continue":
        print(f"Continuing trader bot.")
        pass
    
    else:
        print(f"Exiting trader bot.")
        return

    # Event loop for sell signal
    while True:
        # Calculate the start date
        start_date = datetime.datetime.now() - datetime.timedelta(days=1)
        end_date = datetime.datetime.now()

        # Get historical price data
        ticker_data_15m = get_historical_price_data(symbol, start_date, end_date, "15m")
        ticker_data_60m = get_historical_price_data(symbol, start_date, end_date, "60m")

        # Check if the DataFrames are empty
        if ticker_data_15m.empty or ticker_data_60m.empty:
            print(f"No valid data available for ticker '{symbol}'.")
            return

        # Calculate the moving averages
        ticker_data_15m = calculate_moving_averages(ticker_data_15m, ma_period, ma_period2)
        ticker_data_60m = calculate_moving_averages(ticker_data_60m, ma_period, ma_period2)

        # Get the latest moving average values
        ma_15 = ticker_data_15m['ma_15'].iloc[-1]
        ma_60 = ticker_data_60m['ma_60'].iloc[-1]

        # Print the moving averages
        print(f"15-minute moving average for ${symbol}: {ma_15:.4f}")
        print(f"60-minute moving average for ${symbol}: {ma_60:.4f}")

        # Check if a sell signal is generated
        if ma_15 < ma_60:
            # Place the sell order
            market_order_data = MarketOrderRequest(
                symbol=alpaca_symbol,
                side=OrderSide.SELL,
                qty=buying_power,
                time_in_force=TimeInForce.GTC
            )
            market_order = trading_client.submit_order(order_data=market_order_data)
            print(f"Sell order placed: Selling shares of {alpaca_symbol}")

        # Get the updated account information
        account = trading_client.get_account()
        buying_power = float(account.buying_power)
        print(f"Updated buying power: ${buying_power:.2f}")
        await asyncio.sleep(300)  # Wait 5 minutes

async def main():
    # Insert Alpaca API credentials
    API_KEY = ""
    SECRET_KEY = ""

    # Trading Account (Default on Paper Trading)
    trading_client = TradingClient(API_KEY, SECRET_KEY, paper=True)

    # Buying Power Input
    print("What is your buying/selling power in US dollars?")
    buying_power = float(input())

    # Run the bot
    await run_algorithmic_trading_bot(trading_client, buying_power)

if __name__ == "__main__":
    asyncio.run(main())

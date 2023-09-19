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

# Gets price data from Yahoo Finance
def get_historical_price_data(symbol, start_date, target_ma):
    ticker_data = yf.Ticker(symbol)
    ticker_df = ticker_data.history(
        start=start_date,
        end=datetime.datetime.now(),
        interval=target_ma,
        prepost=True
    )
    return ticker_df

# Calculates moving averages from price data
def calculate_moving_averages(ticker_data, ma_period, ma_period2):
    ma_period = int(ma_period)
    ma_period2 = int(ma_period2)
    ticker_data[f'ma_{ma_period}'] = ticker_data['Close'].rolling(ma_period).mean()
    ticker_data[f'ma_{ma_period2}'] = ticker_data['Close'].rolling(ma_period2).mean()
    return ticker_data

# Calculates start date based on moving average period
def calculate_time(target_ma):
    if "d" in target_ma:
            ma_period = target_ma.replace("d", "")
            start_date = datetime.datetime.now() - datetime.timedelta(days=int(ma_period))
    elif "m" in target_ma:
            ma_period = target_ma.replace("m", "")
            start_date = datetime.datetime.now() - datetime.timedelta(minutes=int(ma_period))
    elif "min" in target_ma:
            ma_period = target_ma.replace("min", "")
            start_date = datetime.datetime.now() - datetime.timedelta(minutes=int(ma_period))
    elif "wk" in target_ma:
            ma_period = target_ma.replace("wk", "")
            start_date = datetime.datetime.now() - datetime.timedelta(weeks=int(ma_period))
    else:
            print("Invalid moving average period. Please try again.")
            exit()
    return [start_date, ma_period]

# Trading Bot
async def run_algorithmic_trading_bot(trading_client, symbol, buying_power, target_ma, target_ma2, refresh_interval):
    # Calculate start dates
    start_date, ma_period = calculate_time(target_ma)
    start_date2, ma_period2 = calculate_time(target_ma2)

    alpaca_symbol = symbol.replace("-", "")

    # Get historical price data
    ticker_data_1 = get_historical_price_data(symbol, start_date, target_ma)
    ticker_data_2 = get_historical_price_data(symbol, start_date2, target_ma)

    # Check if the DataFrames are empty
    if ticker_data_1.empty or ticker_data_2.empty:
        print(f"No valid data available for ticker '{symbol}'.")
        return

    # Calculate the moving averages
    ticker_data_1 = calculate_moving_averages(ticker_data_1, ma_period, ma_period2)
    ticker_data_2 = calculate_moving_averages(ticker_data_2, ma_period2, ma_period2)

    # Get the latest moving average values
    ma_1 = ticker_data_1[f'ma_{ma_period}'].iloc[-1]
    ma_2 = ticker_data_2[f'ma_{ma_period2}'].iloc[-1]

    # Print the moving averages
    print(f"For {symbol}: {target_ma} is {ma_1:.4f} and {target_ma2} is {ma_2:.4f}")

    # Confirmation
    print(f"Would you like to buy {symbol}?")
    print(f"Type yes, no, or continue:")
    confirmation = input()

    # Check if a buy signal is generated
    if buying_power > 0 and confirmation.lower() == "yes":
        # Calculate the quantity based on the current price
        current_price = ticker_data_1['Close'].iloc[-1]
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

    # Loop for sell signal
    while True:
        # Calculate start dates
        start_date, ma_period = calculate_time(target_ma)
        start_date2, ma_period2 = calculate_time(target_ma2)

        alpaca_symbol = symbol.replace("-", "")

        # Get historical price data
        ticker_data_1 = get_historical_price_data(symbol, start_date, target_ma)
        ticker_data_2 = get_historical_price_data(symbol, start_date2, target_ma)

        # Check if the DataFrames are empty
        if ticker_data_1.empty or ticker_data_2.empty:
            print(f"No valid data available for ticker '{symbol}'.")
            return

        # Calculate the moving averages
        ticker_data_1 = calculate_moving_averages(ticker_data_1, ma_period, ma_period2)
        ticker_data_2 = calculate_moving_averages(ticker_data_2, ma_period2, ma_period2)

        # Get the latest moving average values
        ma_1 = ticker_data_1[f'ma_{ma_period}'].iloc[-1]
        ma_2 = ticker_data_2[f'ma_{ma_period2}'].iloc[-1]

        # Print the moving averages
        print(f"For {symbol}: {target_ma} is {ma_1:.4f} and {target_ma2} is {ma_2:.4f}")

        # Check if a sell signal is generated
        if ma_1 < ma_2:
            # Place the sell order
            trading_client.close_all_positions(cancel_orders=True)
            print(f"Sell order placed: Selling shares of {alpaca_symbol}")

        # Get the updated account information and wait for loop
        account = trading_client.get_account()
        buying_power = float(account.buying_power)
        print(f"Updated buying power: ${buying_power:.2f}")
        await asyncio.sleep(refresh_interval)

async def main():
    # Insert Alpaca API credentials
    API_KEY = ""
    SECRET_KEY = ""

    # Trading Account (Default on Paper Trading)
    trading_client = TradingClient(API_KEY, SECRET_KEY, paper=True)

    # Ticker Input
    print("Enter the symbol of the asset you want to trade:")
    print("Example: ETH-USD, AAPL, F")
    symbol = input()

    # Buying Power Input
    print("What is your buying/selling power in US dollars?")
    buying_power = float(input())

    # Target Moving Average Input
    print("What is your target moving averages in days, minutes, or weeks? (Lower timeframes first)")
    print("Example: 15m 60m")
    print("Example: 1d 5d")
    target_ma, target_ma2 = input().split()

    # Refresh Interval Input
    print("How often would you like the bot to refresh data and a sell signal in seconds?")
    print("Example: 300")
    refresh_interval = int(input())

    # Run the bot
    await run_algorithmic_trading_bot(trading_client, symbol, buying_power, target_ma, target_ma2, refresh_interval)

if __name__ == "__main__":
    asyncio.run(main())

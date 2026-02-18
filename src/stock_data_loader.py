import yfinance as yf
import pandas as pd
import numpy as np
import json
import os

def load_stock_config(market='BSE'):
    """Lengths the stock configuration from json file based on market."""
    filename = 'nse_stocks.json' if market == 'NSE' else 'stocks.json'
    config_path = os.path.join(os.path.dirname(__file__), 'config', filename)
    with open(config_path, 'r') as f:
        config = json.load(f)
    return config['stocks']

def fetch_stock_data(ticker, period='10y'):
    """
    Fetches historical data for a single stock.
    Defaults to 10 years of data for robust volatility modeling.
    """
    try:
        data = yf.download(ticker, period=period, progress=False)
        if data.empty:
            print(f"Warning: No data found for {ticker}")
            return None
        
        # Handle MultiIndex columns (Price, Ticker)
        if isinstance(data.columns, pd.MultiIndex):
            try:
                # Extract the dataframe for the specific ticker
                data = data.xs(ticker, axis=1, level=1)
            except KeyError:
                # Fallback if structure is different
                pass
        
        # Keep Closing prices
        df = data[['Close']].copy()
        
        # Calculate Log Returns
        df['Return'] = np.log(df['Close'] / df['Close'].shift(1))

        df.dropna(inplace=True)
        
        return df
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None

if __name__ == "__main__":
    stocks = load_stock_config()
    print(f"Loaded {len(stocks)} stocks from config.")
    
    # Test fetch for first stock
    first_ticker = stocks[0]
    print(f"\nFetching data for {first_ticker}...")
    df = fetch_stock_data(first_ticker)
    if df is not None:
        print(df.head())
        print(df.describe())

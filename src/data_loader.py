import yfinance as yf
import pandas as pd
import numpy as np

def fetch_sensex_data(start_date='2011-04-01', end_date='2020-06-18'):
    """
    Fetches historical data for BSE SENSEX (^BSESN).
    Dates are based on the paper's period: April 01, 2011 - June 17, 2020.
    """
    print(f"Fetching SENSEX data from {start_date} to {end_date}...")
    ticker = "^BSESN"
    data = yf.download(ticker, start=start_date, end=end_date)
    
    if data.empty:
        raise ValueError("No data fetched. Check your internet connection or ticker symbol.")
    
    # Keep only Closing prices as per the paper
    df = data[['Close']].copy()
    
    # Calculate Log Returns: ln(Pt / Pt-1)
    # The paper mentions "continuous returns", which typically implies log returns.
    df['Return'] = np.log(df['Close'] / df['Close'].shift(1))
    
    # Drop NaN values created by shift
    df.dropna(inplace=True)
    
    print(f"Successfully fetched {len(df)} data points.")
    return df

if __name__ == "__main__":
    df = fetch_sensex_data()
    print(df.head())
    print(df.describe())

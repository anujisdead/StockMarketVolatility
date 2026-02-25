import asyncio
import aiohttp
import json
import redis
import numpy as np
import time
import os
from datetime import datetime

# Configuration
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
UPDATE_INTERVAL = 1.0 # seconds

# Redis Connection
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

# Volatility Window (Store last 60 prices per ticker)
price_history = {}

def load_tickers():
    tickers = []
    base_dir = os.path.dirname(__file__)
    
    # Load BSE
    try:
        with open(os.path.join(base_dir, 'config', 'stocks.json'), 'r') as f:
            data = json.load(f)
            tickers.extend(data.get('stocks', []))
    except Exception as e:
        print(f"Error loading BSE stocks: {e}")

    # Load NSE
    try:
        with open(os.path.join(base_dir, 'config', 'nse_stocks.json'), 'r') as f:
            data = json.load(f)
            tickers.extend(data.get('stocks', []))
    except Exception as e:
        print(f"Error loading NSE stocks: {e}")
        
    return list(set(tickers))

async def fetch_yahoo(session, ticker):
    # Yahoo Finance Chart API (Free/Public)
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        async with session.get(url, headers=headers, timeout=0.8) as response:
            if response.status == 200:
                data = await response.json()
                meta = data['chart']['result'][0]['meta']
                price = meta['regularMarketPrice']
                prev_close = meta.get('chartPreviousClose', meta.get('previousClose', price))
                return price, prev_close
    except Exception:
        pass
    return None, None

async def ticker_loop(session, ticker):
    # For now, we rely primarily on Yahoo as the reliable free source.
    price, prev_close = await fetch_yahoo(session, ticker)
    
    if price:
        timestamp = datetime.now().isoformat()
        change_pct = ((price - prev_close) / prev_close) * 100 if prev_close else 0.0
        
        # Publish Price & Change
        msg = json.dumps({
            'ticker': ticker, 
            'price': price, 
            'change_pct': change_pct,
            'time': timestamp
        })
        r.publish('price_feed', msg)
        r.hset('intraday_snapshot', ticker, msg)
        
        # Update History & Calculate Volatility
        history = price_history.get(ticker, [])
        history.append(price)
        if len(history) > 60:
            history.pop(0)
        price_history[ticker] = history
        
        # Calculate 1-minute Volatility (Standard Deviation of RECENT prices)
        # Using a simple formulation for "live volatility": Std Dev of returns in the window
        if len(history) >= 2:
            prices_arr = np.array(history)
            # Log returns for volatility stability
            returns = np.diff(np.log(prices_arr))
            if len(returns) > 0:
                # Annualized Volatility of the last minute (very noisy, but "real-time")
                # Scaling: 1-second ticks -> Year. sqrt(seconds_in_year) approx.
                # Actually, standard practice for "1-minute volatility" might just be the std dev of the prices themselves 
                # or the realized volatility over that minute.
                # Let's provide Annualized Volatility based on the last 60 seconds of 1s returns.
                # Seconds in trading year ~ 6.5 hours * 252 * 60 * 60 approx... 
                # Let's stick to a simpler metric for visual: StdDev of % returns * sqrt(window)
                vol = np.std(returns) * np.sqrt(252 * 375 * 60) # highly annualized
                
                # Capping it to avoid Infinity/NaN on zero variance
                if np.isnan(vol): vol = 0.0
                
                vol_msg = json.dumps({'ticker': ticker, 'volatility': vol, 'time': timestamp})
                r.publish('volatility_feed', vol_msg)

async def main():
    tickers = load_tickers()
    print(f"Starting Price Engine for {len(tickers)} tickers...")
    
    # Initialize history
    for t in tickers:
        price_history[t] = []
        
    async with aiohttp.ClientSession() as session:
        while True:
            start_time = time.time()
            
            # Create tasks for all tickers
            tasks = [ticker_loop(session, t) for t in tickers]
            await asyncio.gather(*tasks)
            
            elapsed = time.time() - start_time
            sleep_time = max(0, UPDATE_INTERVAL - elapsed)
            
            # print(f"Loop time: {elapsed:.2f}s (Sleeping {sleep_time:.2f}s)")
            await asyncio.sleep(sleep_time)

if __name__ == "__main__":
    asyncio.run(main())

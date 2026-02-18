from stock_data_loader import load_stock_config, fetch_stock_data
from models import analyze_stock
from strategy import get_signal
import json
import os
import pandas as pd
from datetime import datetime

def main():
    market = "NSE"
    print(f"--- Starting {market} Stock Analysis Pipeline ---")
    
    # 1. Load Stocks
    stocks = load_stock_config(market=market)
    print(f"Loaded {len(stocks)} stocks.")
    
    results = []
    
    for ticker in stocks:
        print(f"Analyzing {ticker}...")
        
        # 2. Fetch Data
        df = fetch_stock_data(ticker)
        
        if df is None or df.empty:
            results.append({
                'ticker': ticker,
                'signal': 'N/A',
                'reason': 'Data fetch failed',
                'status': 'Error'
            })
            continue
            
        returns = df['Return']
        
        # 3. Analyze (Model + Forecast)
        metrics = analyze_stock(ticker, returns)
        
        # Save detailed data for graph
        if metrics.get('status') == 'Success':
            detail_data = {
                'ticker': ticker,
                'dates': metrics.pop('dates', []),
                'normalized_price': metrics.pop('normalized_price', []),
                'volatility_history': metrics.pop('volatility_history', [])
            }
            stock_dir = os.path.join(os.path.dirname(__file__), 'data', 'stocks')
            os.makedirs(stock_dir, exist_ok=True)
            with open(os.path.join(stock_dir, f"{ticker}.json"), 'w') as f:
                json.dump(detail_data, f)
        
        # 4. Generate Signal
        signal, reason = get_signal(metrics)
        
        # Combine
        # Use .get with default 0.0 or handle safely if 'Close' is missing (unlikely if df not empty)
        last_price = float(df['Close'].iloc[-1]) if not df['Close'].empty else 0.0
        
        result = {
            'ticker': ticker,
            'last_price': last_price,
            'signal': signal,
            'reason': reason,
            **metrics
        }
        results.append(result)
        print(f"-> {ticker}: {signal} ({reason})")

    # 5. Save Results
    output_dir = os.path.join(os.path.dirname(__file__), 'data')
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, 'nse_results.json')
    
    summary = {
        'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'results': results
    }
    
    with open(output_path, 'w') as f:
        json.dump(summary, f, indent=4)
        
    print(f"\nAnalysis complete. Results saved to {output_path}")

if __name__ == "__main__":
    main()

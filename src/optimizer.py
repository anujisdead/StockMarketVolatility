import numpy as np
import pandas as pd
import os
import json
from scipy.optimize import minimize

def get_portfolio_optimization(tickers, market='BSE'):
    """
    Calculates the Minimum Variance Portfolio weights for the selected tickers.
    Uses historical data from the 'data/stocks' directory.
    """
    try:
        data_frames = []
        
        # 1. Load Data
        for ticker in tickers:
            file_path = os.path.join(os.path.dirname(__file__), 'data', 'stocks', f'{ticker}.json')
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    stock_data = json.load(f)
                    
                df = pd.DataFrame({
                    'date': stock_data['dates'],
                    ticker: stock_data['normalized_price']
                })
                df['date'] = pd.to_datetime(df['date'])
                df.set_index('date', inplace=True)
                data_frames.append(df)
        
        if not data_frames:
            return {'error': 'No data found for selected tickers.'}
            
        # 2. Merge Data (Common Dates)
        price_matrix = pd.concat(data_frames, axis=1).dropna()
        if len(price_matrix) < 30:
            return {'error': 'Insufficient overlapping history for optimization.'}
            
        # 3. Calculate Returns & Covariance
        returns = price_matrix.pct_change().dropna()
        cov_matrix = returns.cov() * 252 # Annualized Covariance
        
        # 4. Optimization
        num_assets = len(tickers)
        
        def portfolio_volatility(weights):
            return np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1}) # Weights sum to 1
        bounds = tuple((0.0, 1.0) for asset in range(num_assets)) # No short selling
        
        init_guess = num_assets * [1. / num_assets,]
        
        opt_result = minimize(portfolio_volatility, init_guess, method='SLSQP', bounds=bounds, constraints=constraints)
        
        # 5. Result
        optimal_weights = opt_result.x
        portfolio_vol = opt_result.fun
        
        result_allocation = {}
        for i, ticker in enumerate(price_matrix.columns):
            weight = round(optimal_weights[i] * 100, 2)
            if weight > 0.01: # Filter tiny weights
                result_allocation[ticker] = weight
        
        # Sort by weight
        sorted_allocation = dict(sorted(result_allocation.items(), key=lambda item: item[1], reverse=True))
        
        return {
            'allocation': sorted_allocation,
            'annual_volatility': round(portfolio_vol * 100, 2),
            'message': 'Optimization Successful'
        }
        
    except Exception as e:
        return {'error': str(e)}

def get_signal(metrics):
    """
    Generates a Buy/Sell/Hold signal based on volatility metrics.
    
    Logic:
    - SELL: Forecast Volatility > Current Volatility * 1.05 (Rising Volatility = Risk)
    - BUY: Forecast Volatility < Current Volatility * 0.95 (Falling Volatility = Stability)
    - STRONG SELL: SELL condition + High Gamma (Leverage Effect)
    - CAUTION: HOLD condition + High Gamma
    """
    status = metrics.get('status', 'Error')
    if status != 'Success':
        return 'N/A', f'Analysis Failed: {status}'
    
    current = metrics.get('current_volatility', 0)
    forecast = metrics.get('forecast_volatility', 0)
    gamma = metrics.get('gamma', 0)
    
    signal = "HOLD"
    reason = "Volatility stable"
    
    # 1. Volatility Momentum
    if forecast > current * 1.05:
        signal = "SELL"
        reason = "Volatility rising (>5%)"
    elif forecast < current * 0.95:
        signal = "BUY"
        reason = "Volatility falling (>5%)"
        
    # 2. Leverage Effect (Asymmetry)
    # Gamma > 0 implies bad news increases volatility more than good news
    if gamma > 0.1:
        if signal == "BUY":
            signal = "HOLD" # Cancel buy signal
            reason += " but high leverage risk (Gamma > 0.1)"
        elif signal == "HOLD":
            signal = "CAUTION"
            reason = "High leverage sensitivity to bad news"
        elif signal == "SELL":
            signal = "STRONG SELL"
            reason += " + High leverage risk"
            
    return signal, reason

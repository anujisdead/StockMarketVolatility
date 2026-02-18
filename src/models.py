import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from arch import arch_model
import matplotlib.pyplot as plt

def fit_arma(returns, order=(2, 0, 3)):
    """
    Fits an ARMA model (technically ARIMA(p,0,q)).
    Paper suggests ARMA(2,3).
    """
    print(f"\n--- Fitting ARMA{order} Model ---")
    # suppress warnings for cleaner output
    import warnings
    warnings.filterwarnings("ignore")
    
    model = ARIMA(returns, order=order)
    results = model.fit()
    print(results.summary())
    return results

def fit_best_arma(returns, p_range=range(0, 4), q_range=range(0, 4)):
    """
    Grid search for best ARMA(p,q) based on AIC.
    """
    print("\n--- Finding Best ARMA Model (Grid Search) ---")
    best_aic = float("inf")
    best_order = None
    best_model = None

    import warnings
    warnings.filterwarnings("ignore")

    for p in p_range:
        for q in q_range:
            if p == 0 and q == 0:
                continue
            try:
                model = ARIMA(returns, order=(p, 0, q))
                results = model.fit()
                print(f"ARMA({p},{q}) - AIC: {results.aic}")
                if results.aic < best_aic:
                    best_aic = results.aic
                    best_order = (p, 0, q)
                    best_model = results
            except:
                continue
    
    print(f"\nBest ARMA Order: {best_order} with AIC: {best_aic}")
    return best_model, best_order

def test_arch_effect(residuals):
    """
    Performs ARCH LM test on residuals.
    """
    print("\n--- ARCH LM Test on Residuals ---")
    from statsmodels.stats.diagnostic import het_arch
    # Lagrange multiplier test for autoregressive conditional heteroscedasticity.
    # Returns: lagrange_multiplier_stat, pvalue, fvalue, f_pvalue
    lm_test = het_arch(residuals, ddof=4) # ddof matches lag length or model params roughly
    print(f"LM Statistic: {lm_test[0]}")
    print(f"p-value: {lm_test[1]}")
    print(f"F-Statistic: {lm_test[2]}")
    print(f"F p-value: {lm_test[3]}")
    
    if lm_test[1] < 0.05:
        print("Result: ARCH Effect Present (Reject H0 of no ARCH effect)")
        return True
    else:
        print("Result: No ARCH Effect (Fail to reject H0)")
        return False

def fit_garch(residuals, p=1, q=1):
    """
    Fits GARCH(p,q) model to residuals.
    """
    print(f"\n--- Fitting GARCH({p},{q}) Model ---")
    # rescaling residuals often helps convergence in arch package
    scale = 100
    res_scaled = residuals * scale
    
    # 'GARCH' model with constant mean (Zero mean assumption for residuals of mean equation?)
    # Usually GARCH is fitted on returns directly with mean='Constant' or 'ARX'.
    # But paper implies 2-step: ARMA then GARCH on residuals? 
    # Actually standard practice is joint estimation.
    # However, for replication, if they did step-wise, let's try to mimic or use arch libraries 'ARX' capability.
    
    # Option 1: Fit GARCH on the original *returns* specifying the mean model.
    # The paper says "ARMA(2,3) model is chosen... The conditional mean ARMA(2,3) model equation...".
    # Then "The graph of residuals indicates... ARCH model is to be identified".
    # Then "Therefore, ARCH(1) model matches...".
    # This implies they analyzed residuals of ARMA.
    # But modern `arch` library handles mean and variance jointly best.
    # Let's try fitting GARCH on the *residuals* of ARMA as a zero-mean process first (classic approach)
    # OR better: use arch_model on returns with mean='AR', lags=... but arch_model support for ARMA(p,q) mean is limited (mostly AR).
    
    # Let's stick to fitting on residuals as 'Zero' mean process if we want to follow stepwise strictly, 
    # OR 'Constant' mean if residuals might have non-zero mean (should be ~0).
    
    garch = arch_model(res_scaled, vol='Garch', p=p, q=q, mean='Zero', dist='Normal')
    res = garch.fit(disp='off')
    print(res.summary())
    return res

def fit_tgarch(residuals, p=1, o=1, q=1):
    """
    Fits GJR-GARCH(p,o,q) (Threshold GARCH).
    o=1 implies one threshold term (leverage).
    """
    print(f"\n--- Fitting TGARCH/GJR-GARCH({p},{o},{q}) Model ---")
    scale = 100
    res_scaled = residuals * scale
    
    tgarch = arch_model(res_scaled, vol='Garch', p=p, o=o, q=q, mean='Zero', dist='Normal') # o=1 enables GJR-GARCH
    res = tgarch.fit(disp='off')
    print(res.summary())
    return res

def forecast_volatility(model_result, horizon=5):
    """
    Forecasts volatility using the fitted model.
    Returns the forecast volatility (std dev) for the next 'horizon' days.
    """
    # default method='analytic'
    forecasts = model_result.forecast(horizon=horizon)
    # variance forecast is in forecasts.variance
    # We take the forecast from the last observation
    var_forecast = forecasts.variance.iloc[-1]
    # volatility (std dev)
    vol_forecast = np.sqrt(var_forecast)
    return vol_forecast

def analyze_stock(ticker, returns):
    """
    Runs the full pipeline for a single stock: ARMA -> GARCH/TGARCH -> Forecast.
    Returns a dictionary of metrics.
    """
    metrics = {'ticker': ticker}
    import warnings
    warnings.filterwarnings("ignore")
    
    try:
        # Ensure clean data
        returns = returns.replace([np.inf, -np.inf], np.nan).dropna()
        if len(returns) < 100:
            metrics['status'] = 'Insufficient Data'
            return metrics

        # 1. Fit ARMA(2,3) to get residuals
        # If (2,3) fails to converge, fallback to (1,1) could be added in future
        # For now, we stick to the paper's model
        try:
            arma = ARIMA(returns, order=(2, 0, 3)).fit()
            residuals = arma.resid
        except:
            # Fallback to simpler model
            arma = ARIMA(returns, order=(1, 0, 1)).fit()
            residuals = arma.resid
        
        # 2. Fit TGARCH(1,1) (GJR-GARCH)
        # We use TGARCH as it captures the leverage effect found in Goal 1
        scale = 100
        res_scaled = residuals * scale
        
        # mean='Zero' as we are using residuals from ARMA
        tgarch = arch_model(res_scaled, vol='Garch', p=1, o=1, q=1, mean='Zero', dist='Normal')
        res_tgarch = tgarch.fit(disp='off')
        
        # 3. Forecast
        # Forecast 5 days ahead
        vol_forecast_series = forecast_volatility(res_tgarch, horizon=5)
        # Average forecasted volatility for the next 5 days
        avg_forecast_vol = np.mean(vol_forecast_series.values)
        
        # Current (last estimated) volatility
        current_vol = res_tgarch.conditional_volatility.iloc[-1]
        
        metrics['current_volatility'] = current_vol
        metrics['forecast_volatility'] = avg_forecast_vol
        metrics['gamma'] = res_tgarch.params.get('gamma[1]', 0)
        metrics['alpha'] = res_tgarch.params.get('alpha[1]', 0)
        metrics['beta'] = res_tgarch.params.get('beta[1]', 0)
        metrics['model_aic'] = res_tgarch.aic
        metrics['status'] = 'Success'
        
        # Historical Data
        metrics['dates'] = [d.strftime('%Y-%m-%d') for d in returns.index]
        # Normalized Price (starts at 100)
        metrics['normalized_price'] = [round(p, 2) for p in (np.exp(returns.cumsum()) * 100).tolist()]
        metrics['volatility_history'] = [round(v, 4) for v in res_tgarch.conditional_volatility.tolist()]
        
    except Exception as e:
        metrics['status'] = f'Error: {str(e)}'
        
    return metrics


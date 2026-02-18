import pandas as pd
import numpy as np
from scipy.stats import skew, kurtosis, jarque_bera
from statsmodels.tsa.stattools import adfuller, kpss

def calculate_descriptive_stats(series):
    """
    Computes descriptive statistics: Mean, Median, Std Dev, Skewness, Kurtosis, Jarque-Bera.
    """
    stats = {
        'Mean': np.mean(series),
        'Median': np.median(series),
        'Max': np.max(series),
        'Min': np.min(series),
        'Std Dev': np.std(series),
        'Skewness': skew(series),
        'Kurtosis': kurtosis(series, fisher=False), # Fisher=False for Pearson's definition (normal=3) if needed, paper says >3 means leptokurtic. 
                                                    # scipy defaults to Fisher (normal=0). Let's check paper carefully.
                                                    # Paper says "Kurtosis more than 3 indicates...". This implies Pearson kurtosis (normal=3).
                                                    # scipy.stats.kurtosis calculates Excess Kurtosis (Fisher). So we need to add 3 to match Paper's likely definition or use fisher=False? 
                                                    # Actually scipy.stats.kurtosis(fisher=False) gives Pearson kurtosis.
        'Jarque-Bera': jarque_bera(series)[0],
        'JB Prob': jarque_bera(series)[1],
        'Observations': len(series)
    }
    return stats

def perform_unit_root_test(series):
    """
    Performs Augmented Dickey-Fuller (ADF) test for stationarity.
    """
    print("\n--- Augmented Dickey-Fuller Test ---")
    result = adfuller(series)
    print(f'ADF Statistic: {result[0]}')
    print(f'p-value: {result[1]}')
    print('Critical Values:')
    for key, value in result[4].items():
        print(f'\t{key}: {value}')
    
    is_stationary = result[1] < 0.05
    print(f"Result: The series is {'Stationary' if is_stationary else 'Non-Stationary'}")
    return result

if __name__ == "__main__":
    # Dummy test
    data = np.random.normal(0, 1, 1000)
    print(calculate_descriptive_stats(data))
    perform_unit_root_test(data)

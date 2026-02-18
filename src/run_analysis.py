from data_loader import fetch_sensex_data
from analysis import calculate_descriptive_stats, perform_unit_root_test
import pandas as pd

def main():
    # 1. Fetch Data
    try:
        df = fetch_sensex_data()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return

    returns = df['Return']

    # 2. Descriptive Statistics
    print("\n--- Descriptive Statistics ---")
    stats = calculate_descriptive_stats(returns)
    stats_df = pd.DataFrame(stats, index=[0])
    print(stats_df.transpose())

    # 3. Stationarity Tests
    perform_unit_root_test(returns)

if __name__ == "__main__":
    main()

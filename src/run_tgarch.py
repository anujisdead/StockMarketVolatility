from data_loader import fetch_sensex_data
from models import fit_arma, fit_tgarch
import matplotlib.pyplot as plt

def main():
    # 1. Fetch Data
    try:
        df = fetch_sensex_data()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return

    returns = df['Return']

    # 2. Fit ARMA(2,3) to get residuals
    print("\n--- Fitting ARMA(2,3) to get residuals ---")
    arma_23 = fit_arma(returns, order=(2, 0, 3))
    residuals = arma_23.resid

    # 3. Fit TGARCH(1,1) / GJR-GARCH(1,1,1)
    # The paper refers to it as TGARCH but describes GJR-GARCH (asymmetry term).
    print("\n--- Fitting TGARCH(1,1) (GJR-GARCH) ---")
    tgarch_11 = fit_tgarch(residuals, p=1, o=1, q=1)
    
    # Check for asymmetry (gamma term in GJR-GARCH, often called 'gamma' or 'o' in output)
    print("\n--- Interpretation ---")
    print("Look for the 'gamma[1]' or asymmetry coefficient.")
    print("If significant and positive, it indicates leverage effect (bad news increases volatility more than good news).")
    
    # 4. Plot Conditional Volatility
    plt.figure(figsize=(10, 6))
    plt.plot(tgarch_11.conditional_volatility)
    plt.title('Conditional Volatility (TGARCH(1,1))')
    plt.savefig('tgarch_volatility_plot.png')
    print("TGARCH Volatility plot saved to tgarch_volatility_plot.png")

if __name__ == "__main__":
    main()

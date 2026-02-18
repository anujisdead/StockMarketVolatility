from data_loader import fetch_sensex_data
from models import fit_arma, fit_garch
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

    # 3. Fit ARCH(1)
    print("\n--- Fitting ARCH(1) ---")
    arch_1 = fit_garch(residuals, p=1, q=0) # ARCH(1) corresponds to GARCH(1,0) in some libs, but arch_model treats 'ARCH' differently potentially.
    # In 'arch' package: vol='ARCH', p=1
    from arch import arch_model
    try:
        arch_model_1 = arch_model(residuals * 100, vol='ARCH', p=1, mean='Zero', dist='Normal')
        res_arch_1 = arch_model_1.fit(disp='off')
        print(res_arch_1.summary())
    except Exception as e:
        print(f"Error fitting ARCH(1): {e}")

    # 4. Fit GARCH(1,1)
    print("\n--- Fitting GARCH(1,1) ---")
    garch_11 = fit_garch(residuals, p=1, q=1)
    
    # 5. Plot Conditional Volatility
    plt.figure(figsize=(10, 6))
    plt.plot(garch_11.conditional_volatility)
    plt.title('Conditional Volatility (GARCH(1,1))')
    plt.savefig('volatility_plot.png')
    print("Volatility plot saved to volatility_plot.png")

if __name__ == "__main__":
    main()

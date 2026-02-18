from data_loader import fetch_sensex_data
from models import fit_arma, fit_best_arma, test_arch_effect
import matplotlib.pyplot as plt

def main():
    # 1. Fetch Data
    try:
        df = fetch_sensex_data()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return

    returns = df['Return']

    # 2. Find Best ARMA Model (or just verify ARMA(2,3))
    # Paper uses ARMA(2,3). Let's start with that directly to replicate first.
    # But we can also run grid search as a check.
    # Let's run grid search on small range to see if (2,3) pops up.
    best_results, best_order = fit_best_arma(returns, p_range=range(0, 4), q_range=range(0, 4))
    
    # 3. Fit ARMA(2,3) specifically as per paper if grid search doesn't pick it exactly (data diffs)
    # The paper explicitly states ARMA(2,3) was chosen based on SIC (Schwarz Criterion).
    
    print("\n--- Fitting ARMA(2,3) per Paper ---")
    arma_23 = fit_arma(returns, order=(2, 0, 3))
    
    # Compare AIC/BIC
    print(f"ARMA(2,3) AIC: {arma_23.aic}, BIC: {arma_23.bic}")
    
    # 4. Residual Analysis
    residuals = arma_23.resid
    
    # Plot residuals
    plt.figure(figsize=(10, 6))
    plt.plot(residuals)
    plt.title('Residuals of ARMA(2,3) Model')
    plt.savefig('residuals_plot.png')
    print("Residuals plot saved to residuals_plot.png")
    
    # ARCH LM Test
    test_arch_effect(residuals)

if __name__ == "__main__":
    main()

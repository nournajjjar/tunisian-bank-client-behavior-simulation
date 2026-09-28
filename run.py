# run.py
from model import BankClientModel
import numpy as np

def monte_carlo_simulation(runs=50, steps=24, N=200):
    final_adoption = []
    final_satisfaction = []

    for _ in range(runs):
        model = BankClientModel(N=N, market_scenario="digital_transformation", discount_pct=0.10)
        for _ in range(steps):
            model.step()
        mdf = model.datacollector.get_model_vars_dataframe()
        final_adoption.append(mdf["adoption_rate"].iloc[-1])
        final_satisfaction.append(mdf["avg_satisfaction"].iloc[-1])

    print("Monte Carlo Results")
    print(f"Mean adoption rate: {np.mean(final_adoption):.3f} ± {np.std(final_adoption):.3f}")
    print(f"Mean satisfaction : {np.mean(final_satisfaction):.3f} ± {np.std(final_satisfaction):.3f}")

if __name__ == "__main__":
    monte_carlo_simulation()

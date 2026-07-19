from qiskit_algorithms import QAOA
from qiskit_algorithms.optimizers import COBYLA
from qiskit_optimization.algorithms import MinimumEigenOptimizer
from qiskit.primitives import StatevectorSampler
from quantum_preprocessing import build_portfolio_qubo
from scipy.optimize import minimize
from data import get_financial_data
import numpy as np
import warnings
from scipy.sparse import SparseEfficiencyWarning
import time
import json
from qiskit.circuit.library import QAOAAnsatz
warnings.filterwarnings("ignore", category=SparseEfficiencyWarning)



if __name__=="__main__":
    tickers=["UVXY","WEAT","SQQQ","KOLD","SPY","AAPL","USO"]
    start_date="2025-06-01"
    end_date="2026-07-01"

    expected_returns,covariance_matrix,labels=get_financial_data(tickers,start_date,end_date)
    print("data reading is done")
    data_time=time.time()
    qubo,qp=build_portfolio_qubo(expected_returns,covariance_matrix,risk_aversion=0.5)
    print("qubo imported")
    operator, offset = qubo.to_ising()
    
    sampler=StatevectorSampler()
    cobyla=COBYLA(maxiter=200)

    qaoa=QAOA(sampler=sampler,optimizer=cobyla, reps=1)
    quantum_time=time.time()
    min_eigen=MinimumEigenOptimizer(qaoa)
    end_time=time.time()-quantum_time
    result=min_eigen.solve(qp)
    print(end_time)
    print("Optimal Selection vector : ",result.x)

    selected_indices=[i for i,val in enumerate(result.x) if val==1]
    selected_labels=[labels[i] for i in selected_indices]
    selected_returns=expected_returns[selected_indices]
    selected_covariance=covariance_matrix[selected_indices][:,selected_indices]

    q=0.5

    print(selected_indices)
    print(selected_labels)
    print(selected_returns)
    
    def portfolio_objective(w):
        portfolio_variance = np.dot(w.T, np.dot(selected_covariance, w))

        portfolio_return = np.dot(w.T, selected_returns)
        return (q * portfolio_variance) - portfolio_return

    constraints = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1})
    bounds = [(0, 0.50) for _ in range(len(selected_indices))]
    initial_guess = np.ones(len(selected_indices)) / len(selected_indices)

    opt_res = minimize(portfolio_objective, initial_guess, method='SLSQP', bounds=bounds, constraints=constraints)

    
    final_weights = np.zeros(len(labels))
    for idx, weight in zip(selected_indices, opt_res.x):
        final_weights[idx] = weight

    print(final_weights)
    for ticker, weight in zip(labels, final_weights):
        print(f"Asset: {ticker:<5} | Continuous Weight: {weight:.2%}")

    capital=100000
    investment_per_asset = final_weights * capital

    print("\nCapital Allocation")

    for ticker, invest in zip(labels, investment_per_asset):
        print(f"{ticker:<5} : ₹{invest:.2f}")
    
    asset_profit = investment_per_asset * expected_returns

    final_optimized_weights={ticker : invest for ticker,invest in zip(labels,investment_per_asset)}

    print("expected_profit\n")
    exp_profit=0
    for ticker, profit in zip(labels, asset_profit):
        print(f"{ticker:<5} : ₹{profit:.2f}")
        exp_profit+=profit
    print(f"Capital invested :{capital} got profit:{exp_profit} total value: {capital+exp_profit}")

    portfolio_return=np.dot(final_weights,expected_returns)

    portfolio_variance=np.dot(final_weights.T,np.dot(covariance_matrix,final_weights))
    portfolio_volatility=np.sqrt(portfolio_variance)


    day_profit=0
    for ticker, profit in zip(labels, asset_profit):
        print(f"{ticker:<5} : ₹{profit:.2f}")
        day_profit+=profit
    

    quantum_data={
        "quantum_portfolio_return":portfolio_return,
        "quantum_portfolio_risk":portfolio_volatility,
        "quantum_expected_profit":exp_profit,
        "optimized_weights":final_optimized_weights
    }
    
    with open("quantum_optimization_results.json","w") as f:
        json.dump(quantum_data,f,indent=4)
    old_weights=np.zeros(len(final_weights))
    transaction_cost_per_unit=0.001
    transaction_cost=capital * transaction_cost_per_unit * np.sum(np.abs(final_weights - old_weights))

    print(final_optimized_weights)

    print(final_weights)
    print(portfolio_return)
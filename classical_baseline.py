from scipy.optimize import minimize
import numpy as np
from data import get_financial_data
import matplotlib.pyplot as plt
import json
from quantum_preprocessing import build_portfolio_qubo
from qiskit_optimization.algorithms import CplexOptimizer



def portfolio_performance(weights, expected_returns, cov_matrix):
    portfolio_return=np.dot(weights,expected_returns)

    portfolio_variance=np.dot(weights.T,np.dot(cov_matrix,weights))

    portfolio_volatility=np.sqrt(portfolio_variance)

    return portfolio_return,portfolio_volatility,portfolio_variance

if __name__=='__main__':
    tickers=["UVXY","WEAT","SQQQ","KOLD"]
    start_date="2025-06-01"
    end_date="2026-07-01"

    n_assets=len(tickers)
    expected_returns,cov_matrix,labels=get_financial_data(tickers,start_date,end_date)

    initial_weights = np.ones(len(expected_returns)) / len(expected_returns)

    #obj_results=objective_function(initial_weights, expected_returns, cov_matrix,risk_aversion=0.5)

    qubo,qp=build_portfolio_qubo(expected_returns,cov_matrix,risk_aversion=0.5)

    optimizer=CplexOptimizer(qp)

    opt_result=optimizer.solve(qp)

    print(opt_result.x)

    selected_indices=[i for i,val in enumerate(opt_result.x) if val==1]
    selected_labels=[labels[i] for i in selected_indices]
    selected_returns=expected_returns[selected_indices]
    selected_covariance=cov_matrix[selected_indices][:,selected_indices]
    
    print(selected_indices)
    print(selected_returns)
    print(selected_labels)


    num_selected = len(selected_indices)

    weights = np.zeros(len(labels))
    weights[selected_indices] = 1 / num_selected

    portfolio_return = np.dot(weights, expected_returns)
    portfolio_variance = weights.T @ cov_matrix @ weights
    portfolio_volatility = np.sqrt(portfolio_variance)
    
    optimal_weights_dict = {
    label: float(weight)
    for label, weight in zip(labels, weights)
    }

    capital=100000
    investment = weights * capital
    
    investment_dict = {
    label: float(amount)
    for label, amount in zip(labels, investment)
    }

    print(portfolio_return)
    print(portfolio_variance)

    
    """liquidity = np.array([10, 8, 7, 10])
    constraints = [{
    "type": "eq",
    "fun": lambda w: np.sum(w) - 1
    }
    ]
    constraints.append({
        "type":"ineq",
        "fun":lambda w:np.dot(liquidity,w)-20
    })"""

    """
    bounds = [(0, 0.50)]*n_assets

    optimization_result=minimize(
        objective_function,
        initial_weights,
        args=(expected_returns, cov_matrix, 0.5),
        constraints=constraints,
        bounds=bounds,
        method="SLSQP"
    )
    
    print(optimization_result.success)
    print(optimization_result.message)

    optimal_weights=optimization_result.x   

    portfolio_return, portfolio_volatility,portfolio_variance = portfolio_performance(optimal_weights, expected_returns, cov_matrix)
    optimal_weights_dict={label: float(weight) for label, weight in zip(labels, optimal_weights)}
    print(f"Optimal Portfolio Weights: {optimal_weights_dict}")
    print("=="*25)
    print(f"Optimal Portfolio Return: {portfolio_return}")
    print("=="*25)
    print(f"Optimal Portfolio Volatility: {portfolio_volatility}")

    capital=100000
    investment_values=optimal_weights*capital
    print("=="*25)
    total_income={label : investment for label,investment in zip(labels, investment_values)}

    expected_profit=capital*portfolio_return
    expected_risk=capital*portfolio_volatility
    transaction_cost_rate=0.001
    transaction_costs=transaction_cost_rate * np.sum(np.abs(np.diff(optimal_weights)))
    print("=="*25)
    print(f"Transaction Costs: {transaction_costs}")
    """
    
    
    save_data = {
        "optimal_weights": optimal_weights_dict,
        "portfolio_return": float(portfolio_return),
        "portfolio_volatility": float(portfolio_volatility),
        "investment_values":investment_dict
    }

    with open("optimization_results.json", "w") as f:
        json.dump(save_data, f, indent=4)

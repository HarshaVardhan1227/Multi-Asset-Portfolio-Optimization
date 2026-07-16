from scipy.optimize import minimize
import numpy as np
from data import get_financial_data
import matplotlib.pyplot as plt
import json

def objective_function(weights, expected_returns, cov_matrix,risk_aversion=0.5):
    portfolio_return=np.dot(weights,expected_returns)

    portfolio_variance=np.dot(weights.T,np.dot(cov_matrix,weights))

    


    return -(portfolio_return - risk_aversion * portfolio_variance)


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

    obj_results=objective_function(initial_weights, expected_returns, cov_matrix,risk_aversion=0.5)

    liquidity = np.array([10, 8, 7, 10])
    constraints = [{
    "type": "eq",
    "fun": lambda w: np.sum(w) - 1
    }
    ]
    constraints.append({
        "type":"ineq",
        "fun":lambda w:np.dot(liquidity,w)-20
    })

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

    save_data = {
        "optimal_weights": optimal_weights_dict,
        "portfolio_return": float(portfolio_return),
        "portfolio_volatility": float(portfolio_volatility),
        "investment_values":total_income,
        "expected_profit":expected_profit,
        "expected_risk":expected_risk
    }

    with open("optimization_results.json", "w") as f:
        json.dump(save_data, f, indent=4)

    print(optimal_weights)
    print(expected_returns)
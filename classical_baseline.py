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
    tickers=["NVDA","AAPL","META","AMZN","MSFT"]
    start_date="2025-06-01"
    end_date="2026-07-01"

    n_assets=len(tickers)
    expected_returns,cov_matrix,labels,daily_returns,raw_data,liquidity_scores,transaction_cost_vector=get_financial_data(tickers,start_date,end_date)

    initial_weights = np.ones(len(expected_returns)) / len(expected_returns)

    #obj_results=objective_function(initial_weights, expected_returns, cov_matrix,risk_aversion=0.5)

    qubo,qp=build_portfolio_qubo(expected_returns,cov_matrix,labels,daily_returns,raw_data,liquidity_scores,transaction_cost_vector,risk_aversion=0.5)

    optimizer=CplexOptimizer(qp)

    opt_result=optimizer.solve(qp)

    print(opt_result.status)
    print(opt_result.fval)

    print(opt_result.x)

    selected_indices=[i for i,val in enumerate(opt_result.x) if val==1]
    selected_labels=[labels[i] for i in selected_indices]
    selected_returns=expected_returns[selected_indices]
    selected_covariance=cov_matrix[selected_indices][:,selected_indices]
    selected_transaction_cost=transaction_cost_vector[selected_indices]
    print(selected_indices)
    print(selected_returns)
    print(selected_labels)

    q = 0.5
    eta = 0.02

    old_weights = np.zeros(len(selected_indices))

    def portfolio_objective(w):

        portfolio_return = np.dot(w, selected_returns)

        portfolio_variance = w.T @ selected_covariance @ w

        transaction_cost = np.sum(
            selected_transaction_cost *
            np.abs(w - old_weights)
        )

        return (
            q * portfolio_variance
            - portfolio_return
            + eta * transaction_cost
        )

    constraints = ({
    "type": "eq",
    "fun": lambda w: np.sum(w) - 1
    },)    
    bounds = [(0, 1)] * len(selected_indices)
    initial_guess = np.ones(len(selected_indices)) / len(selected_indices)
    opt_result = minimize(
    portfolio_objective,
    initial_guess,
    method="SLSQP",
    bounds=bounds,
    constraints=constraints
    )

    weights = np.zeros(len(labels))

    for idx, w in zip(selected_indices, opt_result.x):
        weights[idx] = w
    
    print("Weights",weights)
    capital=100000
    investment_per_asset = weights * capital
    
    print("investment per asset",investment_per_asset)
    asset_profit = investment_per_asset * expected_returns

    print("asset",asset_profit)
    optimized_weights={ticker : invest for ticker,invest in zip(labels,investment_per_asset)}

    print("optimized Weights",optimized_weights)

    weight_dict = {
    ticker: weight
    for ticker, weight in zip(labels, weights)
    }

    asset_profit = {
    ticker: float(profit)
    for ticker, profit in zip(labels, investment_per_asset * expected_returns)
    }

    portfolio_return = np.dot(weights, expected_returns)
    portfolio_variance = weights.T @ cov_matrix @ weights
    portfolio_volatility = np.sqrt(portfolio_variance)

    investment_dict = {
    label: float(amount)
    for label, amount in zip(labels, investment_per_asset)
    }

    print("dict",investment_dict)

    
    
    save_data = {
        "optimal_weights": optimized_weights,
        "portfolio_return":portfolio_return,
        "portfolio_volatility":portfolio_volatility,
        "investment_values":investment_dict,
        "capital":capital,
        "weights":weight_dict,
        "assets_profit":asset_profit
    }

    with open("optimization_results.json", "w") as f:
        json.dump(save_data, f, indent=4)

    print(weight_dict)

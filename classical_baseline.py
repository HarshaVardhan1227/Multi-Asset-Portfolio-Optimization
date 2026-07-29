from scipy.optimize import minimize
import numpy as np
from data import get_financial_data
import matplotlib.pyplot as plt
import json
from quantum_preprocessing import build_portfolio_qubo
from qiskit_optimization.algorithms import CplexOptimizer
from asset_mapping import asset_sector


def run_classical_baseline(qubo,qp,labels,expected_returns,cov_matrix,transaction_cost_vector,config):


    optimizer=CplexOptimizer(qp)
    
    opt_result=optimizer.solve(qp)


    """
    print(opt_result.status)
    print(opt_result.fval)
    print(opt_result.x)
    """
    sector_limits = {
            "Technology": config["sector_limits"]["tech_sector_percentage"] / 100,
            "Financial": config["sector_limits"]["finance_sector_percentage"] / 100,
            "Healthcare": config["sector_limits"]["health_sector_percentage"] / 100,
            "Energy & Commodities": config["sector_limits"]["energy_sector_percentage"] / 100,
            "ETFs & Index Funds": config["sector_limits"]["etf_sector_percentage"] / 100,
    }

    selected_indices=[i for i,val in enumerate(opt_result.x) if val==1]
    selected_labels=[labels[i] for i in selected_indices]
    selected_sectors = {}
    for asset in selected_labels:
        sector = asset_sector[asset]
    if sector not in selected_sectors:
        selected_sectors[sector] = sector_limits[sector]
    
    selected_returns=expected_returns[selected_indices]
    selected_covariance=cov_matrix[selected_indices][:,selected_indices]
    selected_transaction_cost=transaction_cost_vector[selected_indices]
    """
    print(selected_indices)
    print(selected_returns)
    print(selected_labels)
    """
    #Renormalize
    total = sum(selected_sectors.values())
    normalized_limits = {}

    for sector, value in selected_sectors.items():
        normalized_limits[sector] = value / total

    q = config["risk_aversion"]
    eta = config["transaction_cost"]

    
    def portfolio_objective(w):
    
        portfolio_return = np.dot(w, selected_returns)
    
        portfolio_variance = w.T @ selected_covariance @ w
    
        transaction_cost = np.sum(
            selected_transaction_cost *
            np.abs(w - initial_guess)
        )
    
        return (q * portfolio_variance- portfolio_return+ eta * transaction_cost)
    
    
    constraints = [
    {
        "type": "eq",
        "fun": lambda w: np.sum(w) - 1
    }
    ] 

    for sector, limit in normalized_limits.items():

        sector_indices = [i for i, ticker in enumerate(selected_labels) if asset_sector[ticker] == sector]

        constraints.append({"type":"ineq", "fun":lambda w,idx=sector_indices,lim=limit:lim - np.sum(w[idx])})

    bounds = [(0, 1)] * len(selected_indices)

    initial_guess = np.ones(len(selected_indices)) / len(selected_indices)

    opt_result = minimize(portfolio_objective,initial_guess, method="SLSQP",bounds=bounds,constraints=constraints)
    
    weights = np.zeros(len(labels))
    
    for idx, w in zip(selected_indices, opt_result.x):
        weights[idx] = w
        
    
    capital=config["capital"]
    investment_per_asset = weights * capital
        
    asset_profit = investment_per_asset * expected_returns
    
    
    investment_weights={ticker : invest for ticker,invest in zip(labels,investment_per_asset)}
    
    
    weight_dict = {ticker: weight for ticker, weight in zip(labels, weights)}
    
    asset_profit = {ticker: float(profit) for ticker, profit in zip(labels, investment_per_asset * expected_returns)}
    
    portfolio_return = np.dot(weights, expected_returns)
    portfolio_variance = weights.T @ cov_matrix @ weights
    portfolio_volatility = np.sqrt(portfolio_variance)
    
    investment_dict = {label: float(amount) for label, amount in zip(labels, investment_per_asset)}
      
        
    save_data = {
        "optimal_weights": investment_weights,
        "portfolio_return":portfolio_return,
        "portfolio_volatility":portfolio_volatility,
        "investment_values":investment_dict,
        "capital":capital,
        "weights":weight_dict,
        "assets_profit":asset_profit,
        "bin_opt":"CPLEX",
        "class_opt":"SLSQP"
    }
    
    with open("optimization_results.json", "w") as f:
        json.dump(save_data, f, indent=4)
    



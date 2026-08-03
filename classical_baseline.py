from scipy.optimize import minimize
import numpy as np
from data import get_financial_data
import matplotlib.pyplot as plt
import json
from quantum_preprocessing import build_portfolio_qubo
from qiskit_optimization.algorithms import CplexOptimizer
from asset_mapping import asset_sector
from objective_analysis import binary_objective_breakdown
from objective_analysis import classical_continuous_breakdown
import time


def run_classical_baseline(qubo,qp,labels,expected_returns,cov_matrix,corr_matrix,transaction_cost_vector,liquidity_scores,config):
    start_time = time.perf_counter()
    optimizer=CplexOptimizer(qp)
    
    opt_result=optimizer.solve(qp)


    """
    print(opt_result.status)
    print(opt_result.fval)
    print(opt_result.x)
    """
    binary_breakdown = binary_objective_breakdown(opt_result.x,expected_returns,cov_matrix,liquidity_scores,transaction_cost_vector,corr_matrix,config)
    sector_limits = {
            "Technology": config["sector_limits"]["tech_sector_percentage"] / 100,
            "Financial": config["sector_limits"]["finance_sector_percentage"] / 100,
            "Healthcare": config["sector_limits"]["health_sector_percentage"] / 100,
            "Energy & Commodities": config["sector_limits"]["energy_sector_percentage"] / 100,
            "ETFs & Index Funds": config["sector_limits"]["etf_sector_percentage"] / 100,
    }

    selected_indices=[i for i,val in enumerate(opt_result.x) if val==1]
    selected_labels=[labels[i] for i in selected_indices]

    required_sectors = {
        sector
        for sector, pct in sector_limits.items()
        if pct > 0
    }

    selected_sector_set = {
        asset_sector[a]
        for a in selected_labels
    }

    missing = required_sectors - selected_sector_set

    if missing:
        print("Missing sectors:", missing)
        
    selected_returns=expected_returns[selected_indices]
    selected_covariance=cov_matrix[selected_indices][:,selected_indices]
    selected_transaction_cost=transaction_cost_vector[selected_indices]
    """
    print(selected_indices)
    print(selected_returns)
    print(selected_labels)
    """
    q = config["risk_aversion"]
    eta = config["transaction_cost"]
    alpha=0.001
    
    def portfolio_objective(w):
    
        portfolio_return = np.dot(w, selected_returns)
    
        portfolio_variance = w.T @ selected_covariance @ w

        unused_cash = 1 - np.sum(w)
    
        transaction_cost = np.sum(
            selected_transaction_cost *
            np.abs(w - initial_guess)
        )
    
        return (q * portfolio_variance- portfolio_return+ eta * transaction_cost+ alpha * unused_cash)
    
    
    constraints = [
    {
        "type": "ineq",
        "fun": lambda w: 1 - np.sum(w)
    }
    ] 



    for sector, limit in sector_limits.items():

        sector_indices = [
            i for i, ticker in enumerate(selected_labels)
            if asset_sector[ticker] == sector
        ]

        # No selected assets from this sector
        if len(sector_indices) == 0:

            # User requested allocation for a missing sector
            if limit > 0:
                print(f"Warning: No selected assets from {sector}.")
            continue

        constraints.append({
            "type": "ineq",
            "fun": lambda w, idx=sector_indices, lim=limit:
                lim - np.sum(w[idx])
        })

    bounds = [(0, 1)] * len(selected_indices)

    initial_guess = np.maximum(selected_returns, 0)

    if initial_guess.sum() == 0:
        initial_guess = np.ones(len(selected_indices))

    initial_guess /= initial_guess.sum()

    opt_result = minimize(portfolio_objective,initial_guess, method="trust-constr",bounds=bounds,constraints=constraints)

    end_time = time.perf_counter()

    execution_time = end_time - start_time

    if not opt_result.success:
        print("SciPy failed:", opt_result.message)

    weights = np.zeros(len(labels))
    old_weights = np.zeros(len(labels))
    
    for idx, w in zip(selected_indices, opt_result.x):
        weights[idx] = w

    continuous_breakdown = classical_continuous_breakdown(
        weights,
        expected_returns,
        cov_matrix,
        transaction_cost_vector,
        old_weights,
        config,
    )
    
    capital=config["capital"]
    investment_per_asset = weights * capital
        
    asset_profit = investment_per_asset * expected_returns
    
    
    investment_weights={ticker : invest for ticker,invest in zip(labels,investment_per_asset)}
    
    opt_selected_labels = [label for label, weight in zip(labels, weights) if weight > 1e-6]
    weight_dict = {ticker: weight for ticker, weight in zip(labels, weights)}
    
    asset_profit = {ticker: float(profit) for ticker, profit in zip(labels, investment_per_asset * expected_returns)}
    
    portfolio_return = np.dot(weights, expected_returns)
    portfolio_variance = weights.T @ cov_matrix @ weights 
    portfolio_volatility = np.sqrt(portfolio_variance)
    
    investment_dict = {label: float(amount) for label, amount in zip(labels, investment_per_asset)}

    invested_fraction = np.sum(weights)
    cash_fraction = 1 - invested_fraction

    invested_capital = invested_fraction * capital
    cash_remaining = cash_fraction * capital
    


    # Final optimized weights
    weights = np.zeros(len(labels))

    for idx, w in zip(selected_indices, opt_result.x):
        weights[idx] = w

    # Total transaction cost
    transaction_cost_rate = config["transaction_cost"]

    total_transaction_cost = (
        config["capital"]
        * transaction_cost_rate
        * np.sum(transaction_cost_vector * np.abs(weights - old_weights))
    )
    
    print(opt_result.status)
    save_data = {
        "optimal_weights": investment_weights,
        "portfolio_return":portfolio_return,
        "portfolio_volatility":portfolio_volatility,
        "investment_values":investment_dict,
        "capital":capital,
        "weights":weight_dict,
        "assets_profit":asset_profit,
        "opt_selected_labels": opt_selected_labels,
        "bin_opt":"CPLEX",
        "class_opt":"TRUST-CONSTR",
        "invested_capital":invested_capital,
        "cash_remaining":cash_remaining,
        "total_transaction_cost":total_transaction_cost,
        "execution_time":float(execution_time),
        "binary_breakdown":binary_breakdown,
        "continuous_breakdown":continuous_breakdown
    }
    
    with open("optimization_results.json", "w") as f:
        json.dump(save_data, f, indent=4)
    



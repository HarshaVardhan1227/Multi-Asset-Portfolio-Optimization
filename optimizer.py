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
from qiskit.visualization import circuit_drawer
warnings.filterwarnings("ignore", category=SparseEfficiencyWarning)
import matplotlib.pyplot as plt
from asset_mapping import asset_sector
from objective_analysis import binary_objective_breakdown, quantum_continuous_breakdown
import psutil
import os

from quantum_setup import qaoa

process = psutil.Process(os.getpid())


def quantum_optimizer(qubo,qp,expected_returns,covariance_matrix,liquidity_scores,labels,daily_returns,transaction_cost_vector,corr_matrix,config):
    print("===== START QUANTUM =====")
    operator, offset = qubo.to_ising()
        
    qaoa_result = qaoa.compute_minimum_eigenvalue(operator)

    print(qaoa_result.eigenvalue)
    print(qaoa_result.optimal_point)
    print(qaoa_result.optimal_parameters)
    print(qaoa_result.best_measurement)
    print("Eigenvalue            :", qaoa_result.eigenvalue)
    print("Optimal Value         :", qaoa_result.optimal_value)
    print("Optimal Point         :", qaoa_result.optimal_point)
    print("Optimal Parameters    :", qaoa_result.optimal_parameters)
    print("Best Measurement      :", qaoa_result.best_measurement)
    print("Optimizer Time        :", qaoa_result.optimizer_time)
    print("Aux Operators         :", qaoa_result.aux_operators_evaluated)
    print("Cost Function Evals   :", qaoa_result.cost_function_evals)
   
    print("QAOA")
    print(qaoa)
    print("=" * 40)
    print(f"Memory BEFORE: {process.memory_info().rss / 1024**2:.2f} MB")
    print("=" * 40)
    min_eigen=MinimumEigenOptimizer(qaoa)
    print("Before solve")
    
    try:
        print(qp.prettyprint())
        start_time = time.perf_counter()
        result = min_eigen.solve(qp)

        print("After solve")
    except Exception as e:
        import traceback

        print(traceback.format_exc())
        raise
    binary_breakdown = binary_objective_breakdown(result.x,expected_returns,covariance_matrix,liquidity_scores,transaction_cost_vector,corr_matrix,config)
    sector_limits = {
                "Technology": config["sector_limits"]["tech_sector_percentage"] / 100,
                "Financial": config["sector_limits"]["finance_sector_percentage"] / 100,
                "Healthcare": config["sector_limits"]["health_sector_percentage"] / 100,
                "Energy & Commodities": config["sector_limits"]["energy_sector_percentage"] / 100,
                "ETFs & Index Funds": config["sector_limits"]["etf_sector_percentage"] / 100,
        }
    
    selected_indices=[i for i,val in enumerate(result.x) if val==1]
    selected_labels=[labels[i] for i in selected_indices]
    required_sectors = {sector for sector, pct in sector_limits.items() if pct > 0}

    selected_sector_set = {
        asset_sector[a]
        for a in selected_labels
    }

    missing = required_sectors - selected_sector_set

    if missing:
        print("Missing sectors:", missing)
    selected_returns=expected_returns[selected_indices]
    selected_covariance=covariance_matrix[selected_indices][:,selected_indices]
    selected_transaction_cost = transaction_cost_vector[selected_indices]
    
    q=config["risk_aversion"]
    eta=config["transaction_cost"]
    alpha = 0.001
    
    def portfolio_objective(w):
        portfolio_variance = np.dot(w.T, np.dot(selected_covariance, w))
    
        portfolio_return = np.dot(w.T, selected_returns)
        portfolio_volatility=np.sqrt(portfolio_variance)
        transaction_cost = np.sum(selected_transaction_cost *np.abs(w - initial_guess))
        unused_cash=1 - np.sum(w)
        return (q * portfolio_variance) - portfolio_return+ eta*transaction_cost+alpha*unused_cash
    
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

        if len(sector_indices) == 0:
            if limit > 0:
                print(f"Warning: No selected assets from {sector}.")
            continue

        constraints.append({
            "type": "ineq",
            "fun": lambda w, idx=sector_indices, lim=limit:
                lim - np.sum(w[idx])
        })
    
    bounds = [(0, 1) for _ in range(len(selected_indices))]
    initial_guess = np.maximum(selected_returns, 0)

    if initial_guess.sum() == 0:
        initial_guess = np.ones(len(selected_indices))

    initial_guess /= initial_guess.sum()
    
    opt_res = minimize(portfolio_objective, initial_guess, method='SLSQP', bounds=bounds, constraints=constraints)
    end_time = time.perf_counter()
    execution_time = end_time - start_time

    objective_value=opt_res.fun
    final_weights = np.zeros(len(labels))
    for idx, weight in zip(selected_indices, opt_res.x):
        final_weights[idx] = weight

    continuous_breakdown = quantum_continuous_breakdown(final_weights,expected_returns,covariance_matrix,transaction_cost_vector,liquidity_scores,np.zeros(len(final_weights)),config)

    for ticker, weight in zip(labels, final_weights):
        print(f"Asset: {ticker:<5} | Continuous Weight: {weight:.2%}")
    
    capital=config["capital"]
    investment_per_asset = final_weights * capital

    investment_per_asset_dict={ticker : invest for ticker,invest in zip(labels,investment_per_asset)}
    invested_fraction = np.sum(final_weights)
    cash_fraction = 1 - invested_fraction

    invested_capital = invested_fraction * capital
    cash_remaining = cash_fraction * capital

    for ticker, invest in zip(labels, investment_per_asset):
        print(f"{ticker:<5} : ₹{invest:.2f}")
        
    asset_profit = investment_per_asset * expected_returns
    
    final_optimized_weights={ticker : invest for ticker,invest in zip(labels,investment_per_asset)}

    asset_profit_dict={ticker : profit for ticker,profit in zip(labels,asset_profit)}
    opt_selected_labels = [label for label, weight in zip(labels, final_weights) if weight > 1e-6]
    
    exp_profit=0
    for ticker, profit in zip(labels, asset_profit):
        print(f"{ticker:<5} : ₹{profit:.2f}")
        exp_profit+=profit

    
    portfolio_return=np.dot(final_weights,expected_returns)
    
    portfolio_variance=np.dot(final_weights.T,np.dot(covariance_matrix,final_weights))
    portfolio_volatility=np.sqrt(portfolio_variance)
    
    
    old_weights = np.zeros(len(final_weights))

    trade_amount = np.abs(final_weights - old_weights)

    transaction_cost_rate = 0.001      # 0.1%

    transaction_cost_per_asset = (
        capital
        * trade_amount
        * transaction_cost_vector
        * transaction_cost_rate
    )

    total_transaction_cost = np.sum(transaction_cost_per_asset)

    transaction_cost_dict = {
        ticker: float(cost)
        for ticker, cost in zip(labels, transaction_cost_per_asset)
    }

    for ticker, cost in zip(labels, transaction_cost_per_asset):
        print(f"{ticker:<5}: ₹{cost:.2f}")
    

    
    for ticker, cost in zip(labels, transaction_cost_per_asset):
        print(f"{ticker:<5}: ₹{cost:.2f}")

    final_weights_dict={ticker : final_weight for ticker,final_weight in zip(labels,final_weights)}
    ansatz = QAOAAnsatz(operator, reps=2)
    opt_layers=str(ansatz.reps)
    circuit_depth=str(ansatz.depth())
    quantum_data={
        "quantum_portfolio_return":portfolio_return,
        "quantum_portfolio_risk":portfolio_volatility,
        "quantum_expected_profit":exp_profit,
        "optimized_weights":final_optimized_weights,
        "opt_selected_labels": opt_selected_labels,
        "total_transaction_cost":float(total_transaction_cost),
        "algo":"QAOA",
        "optimizer":"COBYLA",
        "opt_layers":opt_layers,
        "cir_depth":circuit_depth,
        "capital":capital,
        "investment_per_asset":investment_per_asset_dict,
        "asset_profit_per_asset":asset_profit_dict,
        "selected_assets":opt_selected_labels,
        "invested_capital": float(invested_capital),
        "cash_remaining": float(cash_remaining),
        "obj_value":float(objective_value),
        "normal_weights":final_weights_dict,
        "execution_time":float(execution_time),
        "binary_breakdown":binary_breakdown,
        "continuous_breakdown":continuous_breakdown
    }
        
    with open("quantum_optimization_results.json","w") as f:
        json.dump(quantum_data,f,indent=4)
    old_weights=np.zeros(len(final_weights))
    transaction_cost_per_unit=0.001
    transaction_cost=capital * transaction_cost_per_unit * np.sum(np.abs(final_weights - old_weights))

    print("=" * 40)
    print(f"Memory END: {process.memory_info().rss / 1024**2:.2f} MB")
    print("=" * 40)

    print("Capital:", capital)
    print("Trade Amount:", trade_amount)
    print("Transaction Cost Vector:", transaction_cost_vector)

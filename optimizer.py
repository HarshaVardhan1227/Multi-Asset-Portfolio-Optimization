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
import psutil
import os

from quantum_setup import qaoa

process = psutil.Process(os.getpid())


def quantum_optimizer(qubo,qp,expected_returns,covariance_matrix,labels,daily_returns,transaction_cost_vector,config):
    print("===== START QUANTUM =====")
    operator, offset = qubo.to_ising()
        
    """
    print("=" * 60)
    print("QAOA Problem Statistics")
    print("=" * 60)
    
    print(f"Assets                : {len(labels)}")
    print(f"Binary Variables      : {qubo.get_num_binary_vars()}")
    print(f"Qubits Required       : {operator.num_qubits}")
    
    """
    
    """
    print(ansatz.draw(output="text"))
    
    
    print(f"QAOA Layers (reps)    : {ansatz.reps}")
    print(f"Circuit Depth         : {ansatz.depth()}")
    print(f"Number of Parameters  : {ansatz.num_parameters}")
    
    print("=" * 60)
    """
    print("=" * 40)
    print(f"Memory BEFORE: {process.memory_info().rss / 1024**2:.2f} MB")
    print("=" * 40)
    min_eigen=MinimumEigenOptimizer(qaoa)
    print("Before solve")
    
    try:
        print(qp.prettyprint())
        print(qp.get_num_binary_vars())
        result = min_eigen.solve(qp)
        print("After solve")

    except Exception as e:
        import traceback

        print(traceback.format_exc())
        raise
    print("=" * 40)
    print(f"Memory AFTER QAOA: {process.memory_info().rss / 1024**2:.2f} MB")
    print("=" * 40)
    print("============= END QUANTUM ===========")
    sector_limits = {
                "Technology": config["sector_limits"]["tech_sector_percentage"] / 100,
                "Financial": config["sector_limits"]["finance_sector_percentage"] / 100,
                "Healthcare": config["sector_limits"]["health_sector_percentage"] / 100,
                "Energy & Commodities": config["sector_limits"]["energy_sector_percentage"] / 100,
                "ETFs & Index Funds": config["sector_limits"]["etf_sector_percentage"] / 100,
        }
    
    selected_indices=[i for i,val in enumerate(result.x) if val==1]
    selected_labels=[labels[i] for i in selected_indices]
    selected_sectors = {}
    for asset in selected_labels:
        sector = asset_sector[asset]
    if sector not in selected_sectors:
        selected_sectors[sector] = sector_limits[sector]
    selected_returns=expected_returns[selected_indices]
    selected_covariance=covariance_matrix[selected_indices][:,selected_indices]
    selected_transaction_cost = transaction_cost_vector[selected_indices]
    
    q=config["risk_aversion"]
    eta=config["transaction_cost"]

    #Renormalize
    total = sum(selected_sectors.values())
    normalized_limits = {}
    
    for sector, value in selected_sectors.items():
        normalized_limits[sector] = value / total
    def portfolio_objective(w):
        portfolio_variance = np.dot(w.T, np.dot(selected_covariance, w))
    
        portfolio_return = np.dot(w.T, selected_returns)
        portfolio_volatility=np.sqrt(portfolio_variance)
        transaction_cost = np.sum(selected_transaction_cost *np.abs(w - initial_guess))
        return (q * portfolio_variance) - portfolio_return+ eta*transaction_cost
    
    constraints = [
        {
            "type": "eq",
            "fun": lambda w: np.sum(w) - 1
        }
        ] 

    for sector, limit in normalized_limits.items():
            sector_indices = [i for i, ticker in enumerate(selected_labels) if asset_sector[ticker] == sector]
            constraints.append({"type":"ineq", "fun":lambda w,idx=sector_indices,lim=limit:lim - np.sum(w[idx])})
    
    bounds = [(0, 1) for _ in range(len(selected_indices))]
    initial_guess = np.ones(len(selected_indices)) / len(selected_indices)
    
    opt_res = minimize(portfolio_objective, initial_guess, method='SLSQP', bounds=bounds, constraints=constraints)
    
        
    final_weights = np.zeros(len(labels))
    for idx, weight in zip(selected_indices, opt_res.x):
        final_weights[idx] = weight
    

    for ticker, weight in zip(labels, final_weights):
        print(f"Asset: {ticker:<5} | Continuous Weight: {weight:.2%}")
    
    capital=config["capital"]
    investment_per_asset = final_weights * capital

    investment_per_asset_dict={ticker : invest for ticker,invest in zip(labels,investment_per_asset)}
    
    for ticker, invest in zip(labels, investment_per_asset):
        print(f"{ticker:<5} : ₹{invest:.2f}")
        
    asset_profit = investment_per_asset * expected_returns
    
    final_optimized_weights={ticker : invest for ticker,invest in zip(labels,investment_per_asset)}

    asset_profit_dict={ticker : profit for ticker,profit in zip(labels,asset_profit)}
    
    exp_profit=0
    for ticker, profit in zip(labels, asset_profit):
        print(f"{ticker:<5} : ₹{profit:.2f}")
        exp_profit+=profit

    
    portfolio_return=np.dot(final_weights,expected_returns)
    
    portfolio_variance=np.dot(final_weights.T,np.dot(covariance_matrix,final_weights))
    portfolio_volatility=np.sqrt(portfolio_variance)
    
    
    old_weights = np.zeros(len(final_weights))
    
    trade_amount = np.abs(final_weights - old_weights)
    
    transaction_cost_per_asset = (capital* transaction_cost_vector* trade_amount)
    
    total_transaction_cost = np.sum(transaction_cost_per_asset)
    

    
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
        "total_transaction_cost":float(total_transaction_cost),
        "algo":"QAOA",
        "optimizer":"COBYLA",
        "opt_layers":opt_layers,
        "cir_depth":circuit_depth,
        "capital":capital,
        "investment_per_asset":investment_per_asset_dict,
        "asset_profit_per_asset":asset_profit_dict,
    }
        
    with open("quantum_optimization_results.json","w") as f:
        json.dump(quantum_data,f,indent=4)
    old_weights=np.zeros(len(final_weights))
    transaction_cost_per_unit=0.001
    transaction_cost=capital * transaction_cost_per_unit * np.sum(np.abs(final_weights - old_weights))

    print("=" * 40)
    print(f"Memory END: {process.memory_info().rss / 1024**2:.2f} MB")
    print("=" * 40)



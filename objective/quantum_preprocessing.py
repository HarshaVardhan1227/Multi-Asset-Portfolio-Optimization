from data.data import get_financial_data
from qiskit_optimization import QuadraticProgram
from qiskit_optimization.converters import QuadraticProgramToQubo
import numpy as np
from data.asset_mapping import asset_sector


def build_portfolio_qubo(expected_returns,covariance_matrix,labels,daily_returns,raw_data,liquidity_scores,transaction_cost_vector,config):
    num_assets = len(expected_returns)

    qp=QuadraticProgram()

    for i in range(num_assets):
        qp.binary_var(name=f"x{i}")

    linear={}

    quadratic={}

    risk_aversion = config["risk_aversion"]
    transaction_cost = config["transaction_cost"]
    liquidity_weight = config["liquidity_weight"]
    capital = config["capital"]
    max_assets = config["max_assets"]
    diversification_weight = config["diversification_weight"]
    sector_assets = {
    "Technology": [],
    "Financial": [],
    "Healthcare": [],
    "Energy & Commodities": [],
    "ETFs & Index Funds": []
    }

    for i, asset in enumerate(labels):
        sector = asset_sector[asset]
        sector_assets[sector].append(i)

    sector_limits = {
            "Technology": config["sector_limits"]["tech_sector_percentage"] / 100,
            "Financial": config["sector_limits"]["finance_sector_percentage"] / 100,
            "Healthcare": config["sector_limits"]["health_sector_percentage"] / 100,
            "Energy & Commodities": config["sector_limits"]["energy_sector_percentage"] / 100,
            "ETFs & Index Funds": config["sector_limits"]["etf_sector_percentage"] / 100,
    }

    for i in range(num_assets):
        linear[f"x{i}"] = (
                -expected_returns[i]
                - liquidity_weight * liquidity_scores[i]+transaction_cost*transaction_cost_vector[i]
            )

    for i in range(num_assets):
           for j in range(i,num_assets):            
                quadratic[(f"x{i}",f"x{j}")]=risk_aversion*covariance_matrix[i][j]

    qp.linear_constraint(
            linear={f"x{i}": 1 for i in range(num_assets)},
            sense="==",
            rhs=max_assets,
            name="cardinality"
        )


    std_dev = np.sqrt(np.diag(covariance_matrix))
    correlation_matrix = covariance_matrix / np.outer(std_dev, std_dev)
    correlation_matrix = np.nan_to_num(correlation_matrix)

    lambda_div = diversification_weight

    corr_penalty = np.maximum(correlation_matrix, 0)

    for i in range(num_assets):
        for j in range(i + 1, num_assets):
            quadratic[(f"x{i}", f"x{j}")] = (
                quadratic.get((f"x{i}", f"x{j}"), 0)
                + lambda_div * corr_penalty[i][j]
        )
   


    qp.minimize(linear=linear,quadratic=quadratic)

 
    
    qubo=QuadraticProgramToQubo(penalty=50).convert(qp)
    return qubo,qp

    
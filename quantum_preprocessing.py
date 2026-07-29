from data import get_financial_data
from qiskit_optimization import QuadraticProgram
from qiskit_optimization.converters import QuadraticProgramToQubo
import numpy as np



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
    budget_constraint=config["budget_constraint"]
    liquidity_constraint=config["liquidity_constraint"]
    diversification_constraint=config["diversification"]
    max_assets = config["max_assets"]

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

    lambda_div = 0.05

    for i in range(num_assets):
        for j in range(i + 1, num_assets):
            quadratic[(f"x{i}", f"x{j}")] = (
                quadratic.get((f"x{i}", f"x{j}"), 0)
                + lambda_div * correlation_matrix[i][j]
            )
   


    qp.minimize(linear=linear,quadratic=quadratic)
    
    
    qubo=QuadraticProgramToQubo(penalty=50).convert(qp)
    return qubo,qp

    
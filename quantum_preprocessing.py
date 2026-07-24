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

    diversification_penalty = 0.03

    for i in range(num_assets):
        quadratic[(f"x{i}", f"x{i}")] = (
            quadratic.get((f"x{i}", f"x{i}"), 0)
            + diversification_penalty
        )
   


    qp.minimize(linear=linear,quadratic=quadratic)
    
    
    qubo=QuadraticProgramToQubo(penalty=50).convert(qp)
    return qubo,qp

    
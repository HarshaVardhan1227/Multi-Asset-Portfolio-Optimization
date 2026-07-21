from data import get_financial_data
from qiskit_optimization import QuadraticProgram
from qiskit_optimization.converters import QuadraticProgramToQubo
import numpy as np



def build_portfolio_qubo(expected_returns,covariance_matrix,labels,daily_returns,raw_data,liquidity_scores,transaction_cost_vector,risk_aversion=0.5):
    num_assets = len(expected_returns)

    qp=QuadraticProgram()

    for i in range(num_assets):
        qp.binary_var(name=f"x{i}")

    linear={}

    quadratic={}

    liquidity_weight = 0.05   
    transaction_cost=0.02

    for i in range(num_assets):
        linear[f"x{i}"] = (
            -expected_returns[i]
            - liquidity_weight * liquidity_scores[i]+transaction_cost*transaction_cost_vector[i]
        )

    for i in range(num_assets):
        for j in range(i,num_assets):            
                quadratic[(f"x{i}",f"x{j}")]=risk_aversion*covariance_matrix[i][j]

    """
    qp.linear_constraint(linear={f"x{i}": 1 for i in range(num_assets)}, sense="==", rhs=2, name="budget_constraint")
    """
    qp.minimize(linear=linear,quadratic=quadratic)
    
    
    qubo=QuadraticProgramToQubo(penalty=1000).convert(qp)
    return qubo,qp
    

if __name__=="__main__":
    tickers=["NVDA","AAPL","META","AMZN","MSFT"]
    start_date="2025-06-01"
    end_date="2026-07-01"

    expected_returns,covariance_matrix,labels,daily_returns,raw_data,liquidity_scores,transaction_cost_vector=get_financial_data(tickers,start_date,end_date)


    qubo,qp=build_portfolio_qubo(expected_returns,covariance_matrix,labels,daily_returns,raw_data,liquidity_scores,transaction_cost_vector,risk_aversion=0.5)
    print(qubo.prettyprint())

    print(qp.prettyprint())


    print(liquidity_scores)
    print(transaction_cost_vector)
    
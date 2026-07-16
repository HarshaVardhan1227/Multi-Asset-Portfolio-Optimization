from data import get_financial_data
from qiskit_optimization import QuadraticProgram
from qiskit_optimization.converters import QuadraticProgramToQubo
import numpy as np



def build_portfolio_qubo(expected_returns,covariance_matrix,risk_aversion=0.5):
    num_assets = len(expected_returns)

    qp=QuadraticProgram()

    for i in range(num_assets):
        qp.binary_var(name=f"x{i}")

    linear={}

    quadratic={}

    for i in range(num_assets):
         linear[f"x{i}"]=-(expected_returns[i]-risk_aversion*covariance_matrix[i][i])

    for i in range(num_assets):
        for j in range(num_assets):            
                quadratic[(f"x{i}",f"x{j}")]=risk_aversion*covariance_matrix[i][j]


    qp.linear_constraint(linear={f"x{i}": 1 for i in range(num_assets)}, sense="==", rhs=2, name="budget_constraint")
    liquidity=[11,8,7,10]

    qp.linear_constraint(linear={f"x{i}": liquidity[i] for i in range(num_assets)},sense=">=",rhs=20,name="liquidity_Constraint")
    

    diversification_penalty=0.02

    for i in range(num_assets):
         for j in range(i+1,num_assets):
              quadratic[(f"x{i}", f"x{j}")] = (
                quadratic.get((f"x{i}", f"x{j}"), 0)
                + diversification_penalty
            )
    qp.minimize(linear=linear,quadratic=quadratic)
    
    
    qubo=QuadraticProgramToQubo(penalty=1000).convert(qp)
    return qubo,qp
    

if __name__=="__main__":
    tickers=["UVXY","WEAT","SQQQ","KOLD"]
    start_date="2025-06-01"
    end_date="2026-07-01"

    expected_returns,covariance_matrix,labels=get_financial_data(tickers,start_date,end_date)


    qubo,qp=build_portfolio_qubo(expected_returns,covariance_matrix,risk_aversion=0.5)
    print(qubo.prettyprint())

    print(qp.prettyprint())


    
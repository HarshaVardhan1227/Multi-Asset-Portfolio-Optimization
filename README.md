Multi-Asset Portfolio Optimization using Hybrid Classical-Quantum Computing

Vanguard WISER Quantum Challenge 2026
Challenge Selected
Multi-Asset Portfolio Construction

Team Members
Name	Role	Contribution
Sri Sai Harsha Vardhan Prabhamdhamkam	Quantum Software Developer	Project Design, Mathematical Modeling, QUBO Formulation, Classical Optimization, Quantum Optimization (QAOA), Streamlit Dashboard, Visualization, Documentation

### Project Overview

Portfolio optimization is one of the most important problems in quantitative finance. Investors seek portfolios that maximize expected returns while minimizing investment risk while satisfying practical investment constraints.

Traditional optimization techniques become increasingly computationally expensive as the number of assets and constraints increases. This project explores a hybrid classical-quantum optimization framework where the portfolio optimization problem is transformed into a Quadratic Unconstrained Binary Optimization (QUBO) problem and solved using the Quantum Approximate Optimization Algorithm (QAOA).

The project demonstrates how quantum optimization techniques can assist financial decision-making while maintaining explainability and realistic investment constraints.


### Problem Statement

The objective is to construct an optimal investment portfolio by selecting assets and allocating capital while satisfying practical financial constraints.

The optimization simultaneously considers:

Maximizing Expected Return
Minimizing Portfolio Risk
Minimizing Transaction Costs
Improving Portfolio Liquidity
Encouraging Diversification
Enforcing Budget Constraints
Applying Sector Allocation Limits
Limiting Maximum Number of Assets

The optimization problem is formulated as a Quadratic Unconstrained Binary Optimization (QUBO) model and solved using QAOA.

### Project Objectives
Build a classical Markowitz Portfolio Optimizer
Formulate portfolio optimization as a QUBO problem
Solve the QUBO using QAOA
Compare Classical and Quantum solutions
Build an interactive portfolio dashboard
Demonstrate explainable investment decisions

### Install Required Packages

```bash
pip install numpy
pip install pandas
pip install scipy
pip install matplotlib
pip install plotly
pip install yfinance
pip install pandas-datareader
pip install streamlit
pip install qiskit
pip install qiskit-optimization
pip install qiskit-algorithms
pip install qiskit-ibm-runtime
pip install cplex
pip install openai
pip install google-genai
pip install python-dotenv
```



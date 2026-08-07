### Project Title - Multi-Asset Portfolio Optimization using Hybrid Classical-Quantum Computing

### Vanguard WISER Quantum Challenge 2026<br>

### Challenge Selected - Multi-Asset Portfolio Construction
---
### Team Members and Contributions

| Name | Email | Role | Contribution |
| :--- | :--- | :--- | :--- |
| **Sri Sai Harsha Vardhan Prabhamdhamkam** | harshaworkspace1227@gmail.com | Quantum Optimization and Full Stack Development | Project Design, Mathematical Modeling, QUBO Formulation, Classical Optimization, Quantum Optimization (QAOA), Streamlit Dashboard Development, Visualization, Testing, and Documentation. |
| **Jayadeep Potluri** | jayadeeppotluri@gmail.com | Project Support & Classical Optimization | Financial modeling, classical portfolio optimization, data preprocessing, documentation, testing, result compilation, and presentation preparation. |
---
### Project Overview

Portfolio optimization is one of the most important problems in quantitative finance. Investors seek portfolios that maximize expected returns while minimizing investment risk while satisfying practical investment constraints.

Traditional optimization techniques become increasingly computationally expensive as the number of assets and constraints increases. This project explores a hybrid classical-quantum optimization framework where the portfolio optimization problem is transformed into a Quadratic Unconstrained Binary Optimization (QUBO) problem and solved using the Quantum Approximate Optimization Algorithm (QAOA).

The project demonstrates how quantum optimization techniques can assist financial decision-making while maintaining explainability and realistic investment constraints.

---
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

---

### Project Objectives

* Build a classical Markowitz Portfolio Optimizer<br>
* Formulate portfolio optimization as a QUBO problem<br>
* Solve the QUBO using QAOA<br>
* Compare Classical and Quantum solutions<br>
* Build an interactive portfolio dashboard<br>
* Demonstrate explainable investment decisions<br>

---

### Why We Proposed this Solution
We proposed a hybrid classical-quantum solution because real-world portfolio optimization involves multiple objectives and constraints that become computationally challenging as the number of assets increases. By combining Markowitz optimization for weight allocation with QUBO-based QAOA for asset selection, our approach leverages the strengths of both classical and quantum computing to build diversified, risk-aware, and efficient investment portfolios.

---
### Methods and tools


* **Data Collection:** Retrieved historical market data using Yahoo Finance (`yfinance`).
* **Data Processing:** Calculated expected returns, covariance matrix, volatility, and correlation.
* **Feature Engineering:** Computed liquidity scores, transaction costs, and sector mapping.
* **Portfolio Optimization:** Built a multi-objective model to maximize returns while minimizing risk and transaction costs, and improving liquidity and diversification.
* **Classical Optimization:** Applied Markowitz Mean-Variance Optimization using the SciPy SLSQP optimizer.
* **QUBO Formulation:** Converted the optimization problem into a QUBO model using Qiskit Optimization.
* **Quantum Optimization:** Solved the QUBO using QAOA with the COBYLA optimizer on the Qiskit Aer Statevector Simulator.
* **Evaluation & Visualization:** Compared classical and quantum portfolios using an interactive Streamlit dashboard with performance metrics and visualizations.
---

### Tools and Technologies
| Category | Tools / Libraries |
| :--- | :--- |
| **Programming Language** | Python 3.x |
| **Financial Data** | Yahoo Finance (`yfinance`) |
| **Numerical Computing** | NumPy |
| **Data Processing** | Pandas |
| **Classical Optimization** | SciPy (SLSQP Optimizer) |
| **Quantum Computing** | Qiskit |
| **QUBO Modeling** | Qiskit Optimization |
| **Quantum Algorithm** | QAOA (Quantum Approximate Optimization Algorithm) |
| **Classical Optimizer for QAOA** | COBYLA |
| **Quantum Simulator** | Qiskit Aer Statevector Simulator |
| **Visualization** | Plotly, Matplotlib |
| **Dashboard** | Streamlit |
| **AI Assistant** | Google Gemini API |
| **Version Control** | Git & GitHub |

---

### Project Workflow
<img width="900" height="900" alt="Image" src="https://github.com/user-attachments/assets/893178a7-9469-4c6b-9017-88135645c217" />

## Prerequisites

Before running this project, it is recommended to create and activate a Python virtual environment (`venv`) to isolate project dependencies and avoid conflicts with other Python packages.

### Clone the Repo
```bash
gh repo clone HarshaVardhan1227/Multi-Asset-Portfolio-Optimization
```
---
### Create a Virtual Environment

**Windows**
```bash
python -m venv venv
venv\Scripts\activate
```
---
### Install Required Packages

```bash
pip install streamlit pandas numpy plotly matplotlib seaborn scipy qiskit qiskit-algorithms qiskit-optimization qiskit-aer yfinance Pillow streamlit-javascript reportlab openai google-genai psutil cplex
```
---
### User Interactive Dashboard
## Running the Project

After creating the virtual environment and installing all the required dependencies, launch the interactive Streamlit dashboard using the following command:

```bash
streamlit run app.py
```

This command starts the user-interactive dashboard in your default web browser, where you can:

- Configure portfolio optimization parameters
- Perform Classical and Quantum portfolio optimization
- Compare Classical vs Quantum results
- Analyze portfolio performance and visualizations
- Interact with the AI Portfolio Co-Pilot
---

### Features of this Project
- Hybrid Classical-Quantum Portfolio Optimization
- Multi-Asset Portfolio Construction
- QAOA-based Quantum Asset Selection
- Classical Markowitz Weight Optimization
- Live Portfolio Configuration Dashboard
- Market Analysis and Financial Visualizations
- Classical vs Quantum Performance Comparison
- Portfolio Playground with Live Objective Function
- AI Portfolio Co-Pilot
- Downloadable AI Portfolio Summary Report
- Interactive Streamlit Dashboard

--- 

### Results and Findings
- The implementation successfully demonstrates a hybrid classical-quantum portfolio optimization framework capable of constructing diversified investment portfolios while considering expected return, portfolio risk, transaction costs, liquidity, diversification, and practical investment constraints.

- The project includes comprehensive analytical results, performance comparisons, and dashboard visualizations generated from both the classical and quantum optimization approaches.

- 📂 **All screenshots, visualizations, performance comparisons, and supporting outputs are available in the [`Results`](./Results) folder of this repository.**

---
### Limitations

* **Quantum Simulation:** QAOA is executed on the Qiskit Aer simulator rather than real quantum hardware, so execution times may differ from physical quantum devices.
* **Limited Asset Universe:** The current implementation is evaluated on a limited number of assets due to computational and quantum hardware constraints.
* **Parameter Sensitivity:** Optimization results depend on parameters such as risk aversion, transaction costs, liquidity, diversification, and penalty weights, which require careful tuning.
* **Historical Data Dependency:** Portfolio recommendations are based on historical market data and may not accurately predict future market performance.
* **Current Hardware Constraints:** Existing quantum hardware has limited qubits and is affected by noise, making large-scale portfolio optimization challenging.

---

### Sources and References
- **Markowitz, H. (1952).** *Portfolio Selection*. *The Journal of Finance*, 7(1), 77–91.  
  DOI: https://doi.org/10.1111/j.1540-6261.1952.tb01525.x  
  JSTOR: https://www.jstor.org/stable/2975974

- **Markowitz, H. M. (1959).** *Portfolio Selection: Efficient Diversification of Investments*. Yale University Press.  
  https://archive.org/details/portfolioselecti00mark

- **Farhi, E., Goldstone, J., & Gutmann, S. (2014).** *A Quantum Approximate Optimization Algorithm (QAOA).*  
  arXiv:1411.4028  
  https://arxiv.org/abs/1411.4028
- [Qiskit Documentation](https://qiskit.org/documentation/)
- [Qiskit Optimization Documentation](https://qiskit-community.github.io/qiskit-optimization/)
- [IBM Quantum Documentation](https://docs.quantum.ibm.com/)
- [SciPy Optimization Documentation](https://docs.scipy.org/doc/scipy/reference/optimize.html)
- [SciPy Trust-Constr Optimizer Documentation](https://docs.scipy.org/doc/scipy/reference/optimize.minimize-trustconstr.html)
- [IBM CPLEX Optimizer Documentation](https://www.ibm.com/docs/en/icos)
- [Yahoo Finance (yfinance) Documentation](https://ranaroussi.github.io/yfinance/)
- [Plotly Python Documentation](https://plotly.com/python/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [NumPy Documentation](https://numpy.org/doc/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Matplotlib Documentation](https://matplotlib.org/stable/)
- [Google Gemini API Documentation](https://ai.google.dev/gemini-api/docs)
- Vanguard – WISER Quantum Challenge 2026. Challenge Statement: Multi-Asset Portfolio
Construction. (Project challenge document provided as part of the WISER Quantum
Challenge.)
---
### Required Code, Files, and Reporting Materials

| File / Folder | Description |
|---------------|-------------|
| `app.py` | Main Streamlit application that integrates all modules and provides the interactive dashboard. |
| `data/data.py` | Retrieves historical market data, processes asset prices, and computes financial metrics such as expected returns, covariance, correlation, and volatility. |
| `optimization/classical_baseline.py` | Performs classical portfolio optimization using the Markowitz Mean-Variance model and the SLSQP optimizer. |
| `optimization/quantum_preprocessing.py` | Builds the portfolio optimization model, formulates the QUBO problem, and converts it into an Ising Hamiltonian. |
| `optimization/optimizer.py` | Executes the QAOA algorithm to perform quantum asset selection and optimize the portfolio. |
| `data/asset_mapping.py` | Defines sector mappings, liquidity scores, transaction costs, and asset metadata used in optimization. |
| `app.py` | Generates market analysis visualizations including expected returns, covariance, correlation, efficient frontier, and cumulative returns. |
| `playground/portfolio_objective.py` | Provides an interactive environment for adjusting optimization parameters and computing the live objective function. |
| `copilot/copilot.py` | Implements the AI Portfolio Co-Pilot for portfolio insights, recommendations, and summary generation. |
| `Results/` | Contains dashboard screenshots, comparison charts, performance visualizations, and supporting outputs. |
| `README.md` | Provides complete project documentation, setup instructions, methodology, results, and references. |

---

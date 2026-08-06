### Project Title - Multi-Asset Portfolio Optimization using Hybrid Classical-Quantum Computing

### Vanguard WISER Quantum Challenge 2026<br>

### Challenge Selected - Multi-Asset Portfolio Construction
---
### Team Members and Contributions

| Name | Role | Contribution |
| :--- | :--- | :--- |
| **Sri Sai Harsha Vardhan Prabhamdhamkam** | Quantum Software Developer | Project Design, Mathematical Modeling, QUBO Formulation, Classical Optimization, Quantum Optimization (QAOA), Streamlit Dashboard Development, Visualization, Testing, Documentation |
| **Jayadeep Potluri** | Documentation & Project Support | README Documentation, Repository Organization, Testing, Presentation Preparation, Result Compilation |
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
<img width="1024" height="1536" alt="Image" src="https://github.com/user-attachments/assets/893178a7-9469-4c6b-9017-88135645c217" />

## Prerequisites

Before running this project, it is recommended to create and activate a Python virtual environment (`venv`) to isolate project dependencies and avoid conflicts with other Python packages.

### Create a Virtual Environment

**Windows**
```bash
python -m venv venv
venv\Scripts\activate
```
---
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
pip install google-genai
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

### Results and Findings
--- Home Page

<img width="1800" height="970" alt="Image" src="https://github.com/user-attachments/assets/f98abc9a-f8d4-4224-a58e-bf6e5b372e7b" />

--- Portfolio Configuration

<img width="1871" height="899" alt="Image" src="https://github.com/user-attachments/assets/67a52469-faa5-44d2-96a2-6c50efbdde99" />

<img width="1635" height="859" alt="Image" src="https://github.com/user-attachments/assets/74230c9f-4017-4860-bac6-2d777e12a7eb" />

--- Market Data Analysis

<img width="1701" height="951" alt="Image" src="https://github.com/user-attachments/assets/e323b7bb-e338-48c8-8430-473f0bacd043" />
<img width="1632" height="844" alt="Image" src="https://github.com/user-attachments/assets/18da8f3b-96a0-4a8a-9060-8e4e69dce348" />

--- Classical Portfolio Optimization

<img width="1876" height="909" alt="Image" src="https://github.com/user-attachments/assets/206723eb-1c29-4c25-92d9-47825b169f40" />
<img width="1869" height="890" alt="Image" src="https://github.com/user-attachments/assets/5fa08a00-f87b-4da8-90f1-50bceb44ce41" />
<img width="1800" height="891" alt="Image" src="https://github.com/user-attachments/assets/4c8252fd-76cd-4336-a290-4eb5750e9102" />

--- Quantum Portfolio Optimization

<img width="1866" height="910" alt="Image" src="https://github.com/user-attachments/assets/1e7d2b6c-a53c-487c-bfce-869fed87fc36" />
<img width="1802" height="896" alt="Image" src="https://github.com/user-attachments/assets/8f69510b-e35d-4a65-b5aa-5e94958d8501" />
<img width="1832" height="896" alt="Image" src="https://github.com/user-attachments/assets/f55d72a2-33e5-46ac-a4cd-ebb3bb5bee8b" />
<img width="1822" height="903" alt="Image" src="https://github.com/user-attachments/assets/fad61509-c0d3-4aba-8e95-49d3238cd2eb" />

--- Classical vs Quantum Portfolio Comparision

<img width="1824" height="765" alt="Image" src="https://github.com/user-attachments/assets/b1975133-d229-4815-9269-b1199f6c8b68" />
<img width="1821" height="740" alt="Image" src="https://github.com/user-attachments/assets/5b7e12cf-2b56-4307-825f-c718792318e9" />
<img width="1858" height="737" alt="Image" src="https://github.com/user-attachments/assets/77aa4511-f974-4dba-923e-2026cf24de9f" />

--- Portfolio Playground


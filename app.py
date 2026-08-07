import streamlit as st
from data.data import get_financial_data 
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import datetime
from objective.quantum_preprocessing import build_portfolio_qubo
from data.data import get_financial_data
from optimization.classical_baseline import run_classical_baseline
from optimization.optimizer import quantum_optimizer
import matplotlib.pyplot as plt
import streamlit.components.v1 as components
from copilot.copilot import ai_copilot
from streamlit_javascript import st_javascript
import seaborn as sns
from playground.portfolio_objective import objective_playground
from PIL import Image

import json
st.set_page_config(layout="wide")
st.markdown(
    """
    <p style="margin:0; padding:0;">
       
    </p>
    """,
    unsafe_allow_html=True
)

st.markdown("""
<style>

/* KPI Card */
.kpi-card{
    border-radius:16px;
    padding:18px;
    margin:8px 0;
    box-shadow:0 4px 12px rgba(0,0,0,0.15);
    text-align:center;
    color:white;
    transition:0.3s;
}

.kpi-card:hover{
    transform:translateY(-3px);
    box-shadow:0 8px 18px rgba(0,0,0,0.25);
}

.kpi-title{
    font-size:16px;
    font-weight:600;
    opacity:0.9;
}

.kpi-value{
    font-size:32px;
    font-weight:700;
    margin-top:8px;
}

</style>
""", unsafe_allow_html=True)

def kpi_card(title, value, color):
    st.markdown(
        f"""
        <div class="kpi-card" style="background-color:{color};">
            <div class="kpi-title">{title}</div>
            <div class="kpi-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def scroll_to_top():
    st_javascript(
        "window.parent.scrollTo({top:0, behavior:'smooth'});"
    )

def run_portfolio_optimization(config, tickers,start_date, end_date):
    expected_returns,covariance_matrix,corr_matrix,labels,daily_returns,adj_close_data,liquidity_scores,transaction_cost_vector=get_financial_data(tickers,start_date,end_date)


    qubo, qp = build_portfolio_qubo(
        expected_returns,
        covariance_matrix,
        labels,
        daily_returns,
        adj_close_data,
        liquidity_scores,
        transaction_cost_vector,
        config
    )
    st.success("Objective Function and QUBO Formulation is Done")
    st.session_state["portfolio_data"] = {
        "expected_returns": expected_returns,
        "covariance_matrix": covariance_matrix,
        "corr_matrix": corr_matrix,
        "labels": labels,
        "daily_returns": daily_returns,
        "raw_data": adj_close_data,
        "liquidity_scores": liquidity_scores,
        "transaction_cost_vector": transaction_cost_vector,
        "tickers": tickers,
        "qubo":qubo
    }

    run_classical_baseline(qubo,qp,labels,expected_returns,covariance_matrix,corr_matrix,transaction_cost_vector,liquidity_scores,config)
    st.success("Classical Portfolio Optimization is Done")
    quantum_optimizer(qubo,qp,expected_returns,covariance_matrix,liquidity_scores,labels,daily_returns,transaction_cost_vector,corr_matrix,config)
    st.success("Quantum Portfolio Optimization is Done")
    st.session_state.messages = []

    return qubo,qp

def portfolio_configuration():
    with st.container():
            st.header("⚙️ Portfolio Configurations",text_alignment="center")
            with st.container():
                st.subheader("💰 Investment Capital (₹)")
                col1,col2=st.columns(2)
                with col1:
                    capital = st.number_input(
                        "Choose your Capital",
                        min_value=10000,
                        max_value=100000000,
                        value=100000,
                        step=10000,
                        help="Enter the total amount you wish to invest."
                    )
            with st.container():
                st.subheader("📅 Market Data Period")
                col1,col2=st.columns(2)
                with col1:
                    start_date = st.date_input(
                    "📅 Start Date",
                    value=datetime.date(2025, 6, 1),
                    help="Select the start date for historical market data."
                    )
                with col2:
                    end_date = st.date_input(
                    "📅 End Date",
                    value=datetime.date(2026, 7, 1),
                    help="Select the end date for historical market data."
                    )


            with st.container():
                st.subheader("Portfolio Parameters")
                col1,col2=st.columns(2)
                with col1:
                    st.subheader("📉 Risk Parameters")
                    risk_aversion = st.slider(
                    "📉 Risk Aversion (λ)",
                    min_value=0.0,
                    max_value=1.0,
                    value=0.50,
                    step=0.05,
                    help="Higher values prioritize lower portfolio risk."
                    )
                    st.subheader("💸 Transaction Settings")
                    transaction_cost = st.slider(
                        "Transaction Cost (%)",
                        min_value=0.0,
                        max_value=2.0,
                        value=0.10,
                        step=0.05,
                        help="Estimated trading cost percentage."
                    ) / 100
                with col2:
                    st.subheader("💧 Liquidity Settings")
                    liquidity_weight = st.slider(
                        "Liquidity Weight",
                        min_value=0.0,
                        max_value=1.0,
                        value=0.05,
                        step=0.01,
                        help="Controls the importance of liquidity in portfolio optimization."
                    )

                    st.subheader("🌐 Diversification Settings")
                    diversification_weight = st.slider(
                        "Diversification Weight",
                        min_value=0.0,
                        max_value=1.0,
                        value=0.05,
                        step=0.01,
                        help="Controls the importance of diversification in portfolio optimization."
                    )

            with st.container():
                st.subheader("📊 Asset Selection")

                sector_assets = {
                        "Technology": ["NVDA", "MSFT", "AAPL", "META", "GOOGL"],
                        "Healthcare": ["LLY", "JNJ", "UNH", "PFE", "MRK"],
                        "Financial": ["JPM", "BAC", "GS", "MS", "WFC"],
                        "Energy & Commodities": ["XOM", "CVX", "USO", "KOLD", "GLD"],
                        "ETFs & Index Funds": ["SPY", "QQQ", "DIA", "IWM", "VTI"]
                    }

                selected_assets = []

                with st.container():

                    st.write("Select up to **5 assets** from different sectors.")

                    with st.container():
                        col1,col2=st.columns(2)
                        with col1:
                            st.markdown("### 💻 Technology")
                            tech = st.multiselect(
                                    "Technology Assets",
                                    sector_assets["Technology"],
                                    key="tech"
                                )
                            selected_assets.extend(tech)
                        with col2:
                            st.markdown("### % of Capital Invest in 💻 Technology")
                            tech_pct = st.slider(
                                "💻 Technology",
                                min_value=0,
                                max_value=30,
                                value=15,
                                key="tech_pct"
                            )
                    with st.container():
                        col1,col2=st.columns(2)
                        with col1:
                            st.markdown("### 🏦 Financial")
                            financial = st.multiselect(
                                    "Financial Assets",
                                    sector_assets["Financial"],
                                    key="financial"
                                )
                            selected_assets.extend(financial)
                        with col2:
                            st.markdown("### % of Capital Invest in 🏦 Financial")
                            financial_pct = st.slider(
                                "🏦 Financial",
                                min_value=0,
                                max_value=20,
                                value=5,
                                key="financial_pct"
                            )
                    with st.container():
                        col1,col2=st.columns(2)
                        with col1:
                            st.markdown("### 📈 ETFs")
                            etfs = st.multiselect(
                                "ETF Assets",
                                sector_assets["ETFs & Index Funds"],
                                key="etfs"
                            )
                            selected_assets.extend(etfs)
                        with col2:
                            st.markdown("### % of Capital Invest in 📈 ETFs")
                            etf_pct = st.slider(
                                "📈 ETFs & Index Funds",
                                min_value=0,
                                max_value=15,
                                value=6,
                                key="etf_pct"
                            )

                    with st.container():
                        col1,col2=st.columns(2)

                        with col1:
                            st.markdown("### 🏥 Healthcare")
                            healthcare = st.multiselect(
                                    "Healthcare Assets",
                                    sector_assets["Healthcare"],
                                    key="healthcare"
                                )
                            selected_assets.extend(healthcare)
                        with col2:
                            st.markdown("### % of Capital Invest in 🏥 Healthcare")
                            healthcare_pct = st.slider(
                                "🏥 Healthcare",
                                min_value=0,
                                max_value=20,
                                value=10,
                                key="healthcare_pct"
                            )
                    with st.container():
                        col1,col2=st.columns(2)
                        with col1:
                            st.markdown("### ⚡ Energy & Commodities")
                            energy = st.multiselect(
                                    "Energy Assets",
                                    sector_assets["Energy & Commodities"],
                                    key="energy"
                                )
                            selected_assets.extend(energy)
                        with col2:
                            st.markdown("### % of Capital Invest in ⚡ Energy & Commodities")
                            energy_pct = st.slider(
                                "⚡ Energy & Commodities",
                                min_value=0,
                                max_value=15,
                                value=6,
                                key="energy_pct"
                            )

                    if len(selected_assets) > 5:
                        st.error("⚠️ You can select a maximum of 5 assets.")
                        selected_assets = selected_assets[:5]

                    tickers = selected_assets

                    total_sector_pct = (
                            tech_pct +
                            financial_pct +
                            healthcare_pct +
                            energy_pct +
                            etf_pct
                    )

                    if (
                        tech_pct < 0 or
                        financial_pct < 0 or
                        healthcare_pct < 0 or
                        energy_pct < 0 or
                        etf_pct < 0
                    ):
                        st.error("Sector exposure cannot be negative.")
                        st.stop()
            with st.container():
                st.subheader("Portfolio Constraints")
                col1, col2 = st.columns(2)
                with col1:
                    max_assets = st.slider(
                        "Maximum Number of Assets",
                        min_value=1,
                        max_value=5,
                        value=3,
                        step=1,
                        help="Maximum number of assets that can be included in the optimized portfolio."
                    )
            with st.container():
                run = st.button(
                    "🚀 Run Portfolio Optimization",
                    use_container_width=True,
                    type="primary"
                )

                if run:
                    st.success("Portfolio Optimization Started!")
                
                    config = {
                        "capital": capital,
                        "risk_aversion": risk_aversion,
                        "transaction_cost": transaction_cost,
                        "liquidity_weight":liquidity_weight,
                        "max_assets": max_assets,
                        "diversification_weight":diversification_weight,
                        "sector_limits": {
                            "tech_sector_percentage": tech_pct,
                            "finance_sector_percentage": financial_pct,
                            "health_sector_percentage": healthcare_pct,
                            "energy_sector_percentage": energy_pct,
                            "etf_sector_percentage": etf_pct
                        }
                    }
                
                    st.session_state["config"] = config
                    qubo, qp = run_portfolio_optimization(
                        config,
                        tickers,
                        str(start_date),
                        str(end_date)
                    )

def home_page():
    scroll_to_top()
    with st.container():
        st.title("Multi-Asset Portfolio Optimization using Hybrid Classical-Quantum Computing",text_alignment="center")
        
        st.markdown("""
            Welcome to the **Multi-Asset Portfolio Optimization Dashboard**, an intelligent investment platform that combines
            **Modern Portfolio Theory (Markowitz Model)** with **Quantum Optimization techniques** to construct efficient investment portfolios.

            Financial markets contain thousands of investment opportunities across stocks, ETFs, commodities, and fixed-income assets.
            Selecting the optimal combination while balancing **expected returns**, **risk**, **transaction costs**, and **investment constraints**
            is a complex optimization problem.

            This project addresses that challenge using a **hybrid classical-quantum workflow**:

            - 📊 Classical Optimization using **Markowitz Portfolio Theory**
            - ⚛️ Quantum Optimization using **QUBO (Quadratic Unconstrained Binary Optimization)**
            - 🧮 Portfolio solution through **QAOA (Quantum Approximate Optimization Algorithm)**
            - 📉 Risk analysis using the covariance matrix
            - 💰 Capital allocation and portfolio weight optimization
            - 🔄 Transaction cost modeling
            - 📈 Performance comparison between Classical and Quantum solutions

            The dashboard provides interactive visualizations for financial data analysis,
            portfolio construction, optimization results, and performance evaluation,
            making it easier to understand how quantum computing can assist in solving
            real-world financial optimization problems.
            """)

def details_of_the_assets():
    scroll_to_top()
    if "portfolio_data" not in st.session_state:
        st.warning("Please run portfolio optimization first.")
        return

    data = st.session_state["portfolio_data"]

    expected_returns = data["expected_returns"]
    covariance_matrix = data["covariance_matrix"]
    labels = data["labels"]
    daily_returns = data["daily_returns"]
    raw_data = data["raw_data"]
    tickers = data["tickers"]

    st.header("Market Data Analysis",text_alignment="center")
    expected_returns_series = pd.Series(expected_returns, index=labels)
    
    mapping = {f"Asset {i+1}": ticker for i, ticker in enumerate(tickers)}
    expected_returns = expected_returns_series.rename(index=mapping)

    df_returns = expected_returns.to_frame(name="Expected Return")

    df_returns.index.name = "Ticker"

    with st.container():
        st.write("Expected Asset Returns")

        col1,col2=st.columns([1,2],gap='large')

        with col1:
            st.dataframe(df_returns,width=300)
        with col2:
            colors = ["green" if x >= 0 else "red" for x in expected_returns.values]

            fig = go.Figure(
                data=[
                    go.Bar(
                        x=expected_returns.index,
                        y=expected_returns.values,
                        marker_color=colors,
                        width=0.4
                    )
                ]
            )

            fig.update_layout(
                title="Expected Returns",
                xaxis_title="Assets",
                yaxis_title="Expected Return",
                height=250,
            )

            st.plotly_chart(fig)
        
        with st.container():

            col1,col2=st.columns([1,2],gap='large')
            with col1:
                st.write("Asset Covariance Matrix")
                cov_df = pd.DataFrame(
                covariance_matrix,
                index=tickers,
                columns=tickers
                )

                fig = px.imshow(
                    cov_df,
                    text_auto=".4f",
                    color_continuous_scale="RdBu_r",
                    aspect="auto",
                )

                fig.update_layout(
                    xaxis_title="Assets",
                    yaxis_title="Assets",
                    height=300
                )

                st.plotly_chart(fig, use_container_width=True)
            with col2:
                st.write("Asset Correlation Matrix")

                corr_df = daily_returns.corr()

                fig = px.imshow(
                    corr_df,
                    text_auto=".2f",
                    color_continuous_scale="RdBu_r",
                    aspect="auto"
                )

                fig.update_layout(
                    height=300,
                    xaxis_title="Assets",
                    yaxis_title="Assets"
                )

                st.plotly_chart(fig, use_container_width=True)
        with st.container():
            st.write("Historical Asset Prices")

            fig = px.line(
                raw_data,
                x=raw_data.index,
                y=raw_data.columns,
                labels={
                    "value": "Price",
                    "variable": "Ticker"
                }
            )

            fig.update_layout(
                height=450,
                xaxis_title="Date",
                yaxis_title="Closing Price"
            )

            st.plotly_chart(fig, use_container_width=True)
        with st.container():
            col1,col2=st.columns(2)
            with col1:
                st.subheader("Efficient Frontier Analysis")

                annual_return = daily_returns.mean() * 252

                num_portfolios = 5000

                portfolio_returns = []
                portfolio_risks = []

                for _ in range(num_portfolios):

                    weights = np.random.random(len(tickers))
                    weights /= np.sum(weights)

                    ret = np.dot(weights, annual_return)

                    risk = np.sqrt(
                        np.dot(weights.T,
                            np.dot(covariance_matrix, weights))
                    )

                    portfolio_returns.append(ret)
                    portfolio_risks.append(risk)

                frontier = pd.DataFrame({
                    "Risk": portfolio_risks,
                    "Return": portfolio_returns
                })

                fig = px.scatter(
                    frontier,
                    x="Risk",
                    y="Return",
                    opacity=0.5
                )

                fig.update_layout(
                    height=450,
                    xaxis_title="Portfolio Risk",
                    yaxis_title="Portfolio Return"
                )

                st.plotly_chart(fig, use_container_width=True)
            with col2:
                st.subheader("Annualized Risk vs Return of Individual Assets")
                
                annual_return = daily_returns.mean() * 252
                annual_risk = daily_returns.std() * np.sqrt(252)
                
                risk_df = pd.DataFrame({
                    "Ticker": tickers,
                    "Risk": annual_risk.values,
                    "Return": annual_return.values
                })
                
                fig = px.scatter(
                    risk_df,
                    x="Risk",
                    y="Return",
                    text="Ticker",
                )
                
                fig.update_traces(textposition="top center")
                
                fig.update_layout(
                    height=450,
                    xaxis_title="Annualized Risk",
                    yaxis_title="Annualized Return"
                )
                
                st.plotly_chart(fig, use_container_width=True)
        with st.container():
            st.subheader("Cumulative Asset Returns")
            
            cumulative_returns = (1 + daily_returns).cumprod()
            
            fig = px.line(
                cumulative_returns,
                x=cumulative_returns.index,
                y=cumulative_returns.columns
            )
            
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Portfolio Value",
                height=450,
                hovermode="x unified"
            )
            
            st.plotly_chart(fig, use_container_width=True)
                
def classical_baseline():
    scroll_to_top()
    if "portfolio_data" not in st.session_state:
            st.warning("Please run portfolio optimization first.")
            return
    
    data = st.session_state["portfolio_data"]
    
    expected_returns = data["expected_returns"]
    covariance_matrix = data["covariance_matrix"]
    labels = data["labels"]
    daily_returns = data["daily_returns"]
    raw_data = data["raw_data"]
    tickers = data["tickers"]

    with st.container():
        st.header("📈 Classical Portfolio Optimization",text_alignment="center")
        try:
            with open("json/optimization_results.json", "r") as f:
                saved_results = json.load(f)
            
            
            weights_dict = saved_results["optimal_weights"]
            p_return = saved_results["portfolio_return"]
            p_volatility = saved_results["portfolio_volatility"]
            investment_values=saved_results["investment_values"]
            capital=saved_results["capital"]
            weights=saved_results["weights"]
            asset_profit=saved_results["assets_profit"]
            bin_opt=saved_results["bin_opt"]
            class_opt=saved_results["class_opt"]
            selected_assets=saved_results["opt_selected_labels"]
            invested_capital=saved_results["invested_capital"]
            cash_remaining=saved_results["cash_remaining"]
            binary_objective_breakdown=saved_results["binary_breakdown"]
            continuous_breakdown=saved_results["continuous_breakdown"]



            weight_series = (
                pd.Series(weights)
                .reindex(daily_returns.columns, fill_value=0)
            )

            portfolio_daily_returns = (
                daily_returns.mul(weight_series, axis=1)
            ).sum(axis=1)

            confidence = 0.95

            classical_var = -np.percentile(portfolio_daily_returns,
                                        (1-confidence)*100)

            classical_tail = portfolio_daily_returns[portfolio_daily_returns <= -classical_var]

            classical_cvar = -classical_tail.mean()

            expected_profit=capital*p_return
            m_col1, m_col2,m_col3,m_col4 = st.columns(4)
            with m_col1:
                kpi_card("Expected Return", f"{p_return:.2f}", "#2563EB")
            with m_col2:
                kpi_card("Expected Risk", f"{round(p_volatility,2)}", "#DC2626")
            with m_col3:
                kpi_card("Capital", f"{capital}","#0891B2")
            with m_col4:
                kpi_card("Selected Assets", ",".join(selected_assets), "#7C3AED")
            
            

            with st.container():
                col1,col2,col3,col4=st.columns(4)

                with col1:
                    kpi_card("Binary Optimizer", bin_opt, "#6366F1")
                with col2:
                    kpi_card("Classical Optimizer", class_opt, "#8B5CF6")
                with col3:
                    kpi_card("Invested Capital", round(invested_capital,5), "#16A34A")
                with col4:
                    kpi_card("Remaining Cash", round(cash_remaining,5), "#F59E0B")
            with st.container():
                col1,col2,col3,col4=st.columns(4)
                with col1:
                    kpi_card("Var (95%)", round(classical_var,3), "#EA580C")
                with col2:
                    kpi_card("CVaR (95%)", round(classical_cvar,3),"#DC2626")
                with col3:
                    kpi_card("Expected Profit", round(expected_profit), "#16A34A")
            with st.container():
                col1,col2=st.columns(2)
                with col1:
                    st.subheader("Binary Objective Breakdown")
                    binary_breakdown_df = pd.DataFrame.from_dict(binary_objective_breakdown, orient='index', columns=['Value'])
                    binary_breakdown_df.index.name = 'Component'
                    st.dataframe(binary_breakdown_df)
                with col2:
                    st.subheader("Continuous Objective Breakdown")
                    continuous_breakdown_df = pd.DataFrame.from_dict(continuous_breakdown, orient='index', columns=['Value'])
                    continuous_breakdown_df.index.name = 'Component'
                    st.dataframe(continuous_breakdown_df)
            with st.container():
                col1,col2=st.columns(2,gap="large")
                with col1:
                    invest_weights=pd.DataFrame(list(investment_values.items()),columns=["Ticker","Investment"])
                    fig = px.pie(
                    invest_weights,
                    names="Ticker",
                    values="Investment",
                    title="Portfolio Allocation",
                    )

                    fig.update_layout(
                    width=500,
                    height=400
                    )

                    st.plotly_chart(fig,use_container_width=True)
                with col2:
                    investment_labels = list(investment_values.keys())
                    investment_amounts = list(investment_values.values())
                    fig = px.bar(
                    x=investment_labels,
                    y=investment_amounts,
                    text=investment_amounts,
                    labels={
                        "x": "Assets",
                        "y": "Investment (₹)"
                    },
                    title="Investment Allocation",
                    )

                    fig.update_traces(texttemplate="₹%{y:,.0f}", textposition="outside")

                    fig.update_layout(
                        yaxis_title="Investment (₹)",
                        xaxis_title="Assets"
                    )
                    st.plotly_chart(fig,use_container_width=True)

            with st.container():
                col1,col2=st.columns(2)
                weight_labels = list(weights.keys())
                weight_values = [w * 100 for w in weights.values()]
                with col1:
                    fig = px.bar(
                    x=weight_labels,
                    y=weight_values,
                    text=[f"{w:.1f}%" for w in weight_values],
                    labels={
                        "x": "Assets",
                        "y": "Weight (%)"
                    },
                    title="Portfolio Weight Distribution"
                )

                    fig.update_traces(textposition="outside")

                    fig.update_layout(yaxis=dict(categoryorder="total ascending"))

                    st.plotly_chart(fig,use_container_width=True)
                with col2:
                    profit_labels = list(asset_profit.keys())
                    profit_values = list(asset_profit.values())

                    colors = ["green" if p >= 0 else "red" for p in profit_values]

                    fig = px.bar(
                        x=profit_labels,
                        y=profit_values,
                        text=[f"₹{p:,.2f}" for p in profit_values],
                        title="Expected Profit Per Asset",
                        labels={
                            "x": "Assets",
                            "y": "Expected Profit (₹)"
                        }
                    )

                    fig.update_traces(
                        marker_color=colors,
                        textposition="outside"
                    )

                    st.plotly_chart(fig, use_container_width=True)
            with st.container():
                col1,col2=st.columns(2)
                with col1:
                    cov_df = pd.DataFrame(
                        covariance_matrix,
                        index=tickers,
                        columns=tickers
                    )

                    fig = px.imshow(
                        cov_df,
                        text_auto=".4f",
                        color_continuous_scale="RdBu_r",
                        aspect="auto"
                    )

                    fig.update_layout(
                        title="Covariance Heatmap",
                        xaxis_title="Assets",
                        yaxis_title="Assets",
                        height=450
                    )

                    st.plotly_chart(fig, use_container_width=True)
                with col2:
                    corr_df = daily_returns.corr()
                    fig = px.imshow(
                        corr_df,
                        text_auto=".2f",
                        color_continuous_scale="RdBu_r",
                        aspect="auto"
                    )

                    fig.update_layout(
                        title="Correlation Heatmap",
                        xaxis_title="Assets",
                        yaxis_title="Assets",
                        height=450
                    )

                    st.plotly_chart(fig, use_container_width=True)
            with st.container():
                col1,col2=st.columns(2)
                with col1:
                    st.subheader("Sharpe Ratio")
                    risk_free_rate = 0.05   # 5%

                    # Optimized portfolio weights
                    weight_series = pd.Series(weights).reindex(tickers, fill_value=0)
                    weights_array = weight_series.values

                    portfolio_return = np.dot(expected_returns, weights_array)
                    portfolio_risk = np.sqrt(
                        np.dot(weights_array.T, np.dot(covariance_matrix, weights_array))
                    )

                    sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_risk

                    if sharpe_ratio < 0:
                        color = "red"
                        status = "Poor"
                    elif sharpe_ratio < 1:
                        color = "orange"
                        status = "Average"
                    elif sharpe_ratio < 2:
                        color = "green"
                        status = "Good"
                    else:
                        color = "darkgreen"
                        status = "Excellent"

                    fig = go.Figure(go.Indicator(
                        mode="number+gauge+delta",
                        value=sharpe_ratio,
                        delta={"reference": 1},
                        title={"text": f"Sharpe Ratio<br><span style='font-size:16px'>{status}</span>"},
                        gauge={
                            "axis": {"range": [-1, 3]},
                            "bar": {"color": color},
                            "steps": [
                                    {"range": [-1, 0], "color": "#ff4d4d"},
                                    {"range": [0, 1], "color": "#ffd54f"},
                                    {"range": [1, 2], "color": "#90ee90"},
                                    {"range": [2, 3], "color": "#00c853"},
                            ]
                        }
                    ))

                    fig.update_layout(height=420)

                    st.plotly_chart(fig, use_container_width=True)
                with col2:
                    weight_series = (
                        pd.Series(weights)
                        .reindex(daily_returns.columns, fill_value=0)
                    )

                    portfolio_daily_returns = (
                        daily_returns.mul(weight_series, axis=1)
                    ).sum(axis=1)

                    portfolio_growth = (1 + portfolio_daily_returns).cumprod() * capital

                    growth_df = pd.DataFrame({
                        "Date": portfolio_growth.index,
                        "Portfolio Value": portfolio_growth.values
                    })

                    fig = px.line(
                        growth_df,
                        x="Date",
                        y="Portfolio Value",
                        title="Cumulative Portfolio Growth"
                    )

                    st.plotly_chart(fig, use_container_width=True)
            with st.container():
                col1,col2=st.columns(2)
                with col1:
                    weight_series = pd.Series(weights)
                    weight_series = weight_series.reindex(tickers, fill_value=0)
                    weights_array = weight_series.values

                    portfolio_variance = np.dot(
                        weights_array.T,
                        np.dot(covariance_matrix, weights_array)
                    )

                    marginal_risk = np.dot(covariance_matrix, weights_array)

                    risk_contribution = (
                        weights_array * marginal_risk
                    ) / portfolio_variance

                    risk_df = pd.DataFrame({
                        "Ticker": daily_returns.columns,
                        "Risk Contribution": risk_contribution
                    })

                    fig = px.bar(
                        risk_df,
                        x="Ticker",
                        y="Risk Contribution",
                        text_auto=".2%",
                        title="Risk Contribution by Asset"
                    )

                    st.plotly_chart(fig, use_container_width=True)
                with col2:
                    weight_series = pd.Series(weights).reindex(tickers, fill_value=0)
                    asset_risk = daily_returns.std() * np.sqrt(252)
                    asset_return = expected_returns
                    scatter_df = pd.DataFrame({
                        "Ticker": tickers,
                        "Return": asset_return,
                        "Risk": asset_risk,
                        "Weight": weight_series.values * 100
                    })

                    fig = px.scatter(
                        scatter_df,
                        x="Risk",
                        y="Return",
                        color="Return",
                        size="Weight",
                        text="Ticker",
                        color_continuous_scale="RdYlGn",
                        hover_data=["Weight"],
                        title="Risk vs Return of Assets"
                    )

                    fig.update_traces(textposition="top center")

                    st.plotly_chart(fig, use_container_width=True)
            with st.container():
                col1,col2=st.columns(2)
                with col1:
                    treemap_df = pd.DataFrame({
                        "Ticker": list(investment_values.keys()),
                        "Investment": list(investment_values.values()),
                        "Profit": [asset_profit[t] for t in investment_values.keys()]
                    })

                    fig = px.treemap(
                        treemap_df,
                        path=["Ticker"],
                        values="Investment",
                        color="Profit",
                        color_continuous_scale="RdYlGn",
                        title="Portfolio Allocation by Expected Profit"
                    )

                    fig.update_traces(
                        textinfo="label+value+percent root",
                        hovertemplate=
                            "<b>%{label}</b><br>"
                            "Investment: ₹%{value:,.0f}<br>"
                            "Expected Profit: %{color:,.2f}<extra></extra>"
                    )

                    fig.update_layout(
                        height=500,
                        margin=dict(t=50, l=10, r=10, b=10)
                    )

                    st.plotly_chart(fig, use_container_width=True)
        except FileNotFoundError:
            st.error("Optimization file not found! Please run your backend script first to generate optimization_results.json.")
        
def quantum_portfolio_objectives():
    scroll_to_top()
    if "portfolio_data" not in st.session_state:
        st.warning("Please run portfolio optimization first.")
        return
    
    data = st.session_state["portfolio_data"]
    
    expected_returns = data["expected_returns"]
    covariance_matrix = data["covariance_matrix"]
    labels = data["labels"]
    daily_returns = data["daily_returns"]
    raw_data = data["raw_data"]
    tickers = data["tickers"]
    qubo=data["qubo"]
    st.header("🚀 Quantum Portfolio Optimization",text_alignment="center")
    with st.container():
        try:
            with open("json/quantum_optimization_results.json","r") as f:
                result=json.load(f)
               
            
            portfolio_return=result["quantum_portfolio_return"]
            portfolio_risk=result["quantum_portfolio_risk"]
            portfolio_profit=result["quantum_expected_profit"]
            portfolio_weights_dict=result["optimized_weights"]
            capital=result["capital"]
            transaction_cost=result["total_transaction_cost"]
            algorithm=result["algo"]
            optimizer=result["optimizer"]
            circuit_layers=result["opt_layers"]
            investment_per_asset=result["investment_per_asset"]
            circuit_depth=result["cir_depth"]
            risk_free_rate = 0.05
            sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_risk
            expected_profit = capital * portfolio_return
            asset_profit=result["asset_profit_per_asset"]
            selected_assets=result["selected_assets"]
            capital_invested=result["invested_capital"]
            remaining_cash=result["cash_remaining"]
            obj_value=result["obj_value"]
            normal_weights=result["normal_weights"]
            quantum_execution_time=result["execution_time"]
            binary_objective_breakdown=result["binary_breakdown"]
            continuous_breakdown=result["continuous_breakdown"]
        

            weights = (
                pd.Series(normal_weights)
                .reindex(daily_returns.columns, fill_value=0)
            )

            portfolio_daily_returns = (
                daily_returns.mul(weights, axis=1)
            ).sum(axis=1)

            confidence=0.95
            quantum_var = -np.percentile(portfolio_daily_returns,(1-confidence)*100)

            quantum_tail = portfolio_daily_returns[
                portfolio_daily_returns <= -quantum_var
            ]

            quantum_cvar = -quantum_tail.mean()
            
            col_1,col_2,col_3,col_4=st.columns(4)
            with col_1:
                kpi_card("Portfolio Return", round(portfolio_return,3), "#2563EB")
            with col_2:
                kpi_card("Portfolio Risk", round(portfolio_risk,3),"#DC2626")
            with col_3:
                kpi_card("Expected Profit", int(portfolio_profit),"#16A34A")
            with col_4:
                kpi_card("Expected Risk", int(round(portfolio_risk*100000,3)), "#B91C1C")
            with st.container():
                col1,col2,col3,col4=st.columns(4,gap="large")
                with col1:
                    kpi_card("Algorithm", algorithm,"#7C3AED")
                with col2:
                    kpi_card("Optimizer", optimizer, "#6366F1")
                with col3:
                    kpi_card("Layers", circuit_layers, "#0891B2")
                with col4:
                    kpi_card("Circuit Depth", circuit_depth,"#0F766E")
            with st.container():
                col1,col2,col3,col4=st.columns(4)
                with col1:
                    kpi_card("Capital Invested", round(capital_invested,5), "#16A34A")
                with col2:
                    kpi_card("Remaining Cash", round(remaining_cash,5),"#F59E0B")
                with col3:
                    kpi_card("Transaction Cost", round(transaction_cost,3), "#D97706")
                with col4:
                    kpi_card("Objective Value", round(obj_value,3),"#1F2937")
            with st.container():
                col1,col2,col3,col4=st.columns(4)
                with col1:
                    kpi_card("Var (95%)", round(quantum_var,3),"#EA580C")
                with col2:
                    kpi_card("CVaR (95%)", round(quantum_cvar,3), "#DC2626")
                with col3:
                    kpi_card("Execution Time (s)", round(quantum_execution_time,3),"#4B5563")
                with col4:
                    kpi_card("Selected Assets", ",".join(selected_assets), "#7C3AED")
            with st.container():
                col1,col2=st.columns(2)
                with col1:
                    st.subheader("Binary Objective Breakdown")
                    binary_breakdown_df = pd.DataFrame.from_dict(binary_objective_breakdown, orient='index', columns=['Value'])
                    binary_breakdown_df.index.name = 'Component'
                    st.dataframe(binary_breakdown_df)
                with col2:
                    st.subheader("Continuous Objective Breakdown")
                    continuous_breakdown_df = pd.DataFrame.from_dict(continuous_breakdown, orient='index', columns=['Value'])
                    continuous_breakdown_df.index.name = 'Component'
                    st.dataframe(continuous_breakdown_df)
            with st.container():
                col1,col2=st.columns(2)
                with col1:
                    portfolio_weights=pd.DataFrame(list(portfolio_weights_dict.items()),columns=["Ticker","Investment"])
                    fig = px.pie(
                    portfolio_weights,
                    names="Ticker",
                    values="Investment",
                    title="Portfolio Allocation",
                    )

                    fig.update_layout(
                    width=500,
                    height=400
                    )

                    st.plotly_chart(fig,use_container_width=True)
                with col2:
                    fig = go.Figure()

                    fig.add_trace(go.Scatter(
                        x=[portfolio_risk],
                        y=[portfolio_return],
                        mode="markers+text",
                        text=["Optimized Portfolio"],
                        textposition="top center",
                        marker=dict(size=18)
                    ))

                    fig.update_layout(
                        title="Portfolio Risk vs Return",
                        xaxis_title="Portfolio Risk (Volatility)",
                        yaxis_title="Expected Return",
                        template="plotly_white"
                    )

                    st.plotly_chart(fig,use_container_width=True)
            with st.container():
                col1,col2=st.columns(2)
                with col1:
                    weights = pd.Series(portfolio_weights_dict)

                    weights = weights.reindex(daily_returns.columns).fillna(0)

                    portfolio_daily_return = daily_returns.dot(weights)

                    initial_investment = 100000

                    portfolio_growth = initial_investment * (1 + portfolio_daily_return).cumprod()

                    fig = go.Figure()

                    fig.add_trace(go.Scatter(
                        x=portfolio_growth.index,
                        y=portfolio_growth.values,
                        mode="lines",
                        fill="tozeroy",
                        name="Portfolio Value"
                        ))

                    fig.update_layout(
                        title="Portfolio Growth Over Time",
                        xaxis_title="Date",
                        yaxis_title="Portfolio Value (₹)",
                        template="plotly_white",
                        hovermode="x unified",
                        height=500
                    )

                    st.plotly_chart(fig, use_container_width=True)
                with col2:
                    rolling_max = portfolio_growth.cummax()

                    drawdown = (portfolio_growth - rolling_max) / rolling_max * 100

                    fig = go.Figure()

                    fig.add_trace(go.Scatter(
                        x=drawdown.index,
                        y=drawdown.values,
                        fill="tozeroy",
                        mode="lines",
                        line=dict(color="red"),
                        name="Drawdown"
                    ))

                    fig.update_layout(
                        title="Portfolio Drawdown",
                        xaxis_title="Date",
                        yaxis_title="Drawdown (%)",
                        template="plotly_white",
                        height=500
                    )

                    st.plotly_chart(fig, use_container_width=True)
            with st.container():
                col1,col2=st.columns(2)
                with col1:
                    rolling_volatility = (
                    portfolio_daily_return
                    .rolling(window=30)
                    .std()
                    * np.sqrt(252)
                )

                fig = go.Figure()

                fig.add_trace(go.Scatter(
                    x=rolling_volatility.index,
                    y=rolling_volatility.values,
                    mode="lines",
                    line=dict(color="orange"),
                    name="30-Day Rolling Volatility"
                ))

                fig.update_layout(
                    title="Rolling Portfolio Volatility",
                    xaxis_title="Date",
                    yaxis_title="Annualized Volatility",
                    template="plotly_white",
                    hovermode="x unified",
                    height=500
                )

                st.plotly_chart(fig, use_container_width=True)
            with st.container():
                col1,col2=st.columns(2)
                with col1:
                    cov_df = pd.DataFrame(
                    covariance_matrix,
                    index=tickers,
                    columns=tickers
                    )

                    fig = px.imshow(
                        cov_df,
                        text_auto=".4f",
                        color_continuous_scale="RdBu_r",
                        aspect="auto"
                    )

                    fig.update_layout(
                        title="Covariance Matrix",
                        xaxis_title="Assets",
                        yaxis_title="Assets",
                        height=450
                    )

                    st.plotly_chart(fig, use_container_width=True)
                with col2:
                    corr_df = daily_returns.corr()

                    fig = px.imshow(
                        corr_df,
                        text_auto=".2f",
                        color_continuous_scale="RdBu_r",
                        aspect="auto"
                    )

                    fig.update_layout(
                        title="Correlation Matrix",
                        xaxis_title="Assets",
                        yaxis_title="Assets",
                        height=450
                    )

                    st.plotly_chart(fig, use_container_width=True)
            with st.container():
                col1,col2=st.columns(2)
                with col1:
                    st.subheader("Efficient Frontier")

                    num_portfolios = 3000
                    results = np.zeros((2, num_portfolios))

                    returns = daily_returns.mean() * 252
                    cov = daily_returns.cov() * 252

                    random_returns = []
                    random_risks = []

                    for i in range(num_portfolios):
                        weights = np.random.random(len(returns))
                        weights /= np.sum(weights)

                        port_return = np.sum(weights * returns)
                        port_risk = np.sqrt(np.dot(weights.T, np.dot(cov, weights)))

                        random_returns.append(port_return)
                        random_risks.append(port_risk)

                    fig = go.Figure()

                    fig.add_trace(go.Scatter(
                        x=random_risks,
                        y=random_returns,
                        mode="markers",
                        marker=dict(
                            size=4,
                            color=random_returns,
                            colorscale="Viridis",
                            showscale=True
                        ),
                        name="Random Portfolios"
                    ))

                    fig.add_trace(go.Scatter(
                        x=[portfolio_risk],
                        y=[portfolio_return],
                        mode="markers",
                        marker=dict(
                            color="red",
                            size=15,
                            symbol="star"
                        ),
                        name="Quantum Portfolio"
                    ))

                    st.plotly_chart(fig, use_container_width=True)
                with col2:
                    weights = pd.Series(portfolio_weights_dict)

                    weights = weights.reindex(
                        daily_returns.columns
                    ).fillna(0)

                    cov = daily_returns.cov()*252

                    portfolio_variance = np.dot(
                        weights.T,
                        np.dot(cov,weights)
                    )

                    marginal = cov.dot(weights)

                    contribution = weights*marginal

                    risk_contribution = contribution/portfolio_variance

                    risk_df = pd.DataFrame({

                    "Ticker":risk_contribution.index,

                    "Risk":risk_contribution.values

                    })

                    fig = px.bar(

                    risk_df,

                    x="Ticker",

                    y="Risk",

                    title="Risk Contribution by Asset",

                    color="Risk"

                    )

                    st.plotly_chart(fig,use_container_width=True)
            with st.container():
                col1,col2=st.columns(2)
                with col1:
                    investment_values_of_weights=[investment_per_asset[label] for label in labels]
                    df = pd.DataFrame({
                        "Asset": labels,
                        "Investment": investment_values_of_weights
                    })

                    fig = px.bar(
                        df,
                        x="Asset",
                        y="Investment",
                        color="Investment",
                        text_auto=".2s",
                        title="Capital Allocation Across Assets"
                    )

                    fig.update_layout(
                        xaxis_title="Assets",
                        yaxis_title="Investment (₹)",
                        template="plotly_white"
                    )

                    st.plotly_chart(fig, use_container_width=True)
                with col2:
                    profit_values = [asset_profit[label] for label in labels]
                    df = pd.DataFrame({
                        "Asset": labels,
                        "Profit": profit_values
                    })

                    colors = np.where(df["Profit"] >= 0, "Profit", "Loss")

                    df["Type"] = colors

                    fig = px.bar(
                        df,
                        x="Asset",
                        y="Profit",
                        color="Type",
                        text_auto=".2f",
                        title="Expected Profit per Asset"
                    )

                    fig.update_layout(
                        xaxis_title="Assets",
                        yaxis_title="Expected Profit (₹)",
                        template="plotly_white"
                    )

                    st.plotly_chart(fig, use_container_width=True)
            with st.container():
                asset_risk = np.sqrt(np.diag(covariance_matrix))
                df = pd.DataFrame({
                        "Asset": labels,
                        "Risk": asset_risk,
                        "Return": expected_returns
                })

                fig = px.scatter(
                        df,
                        x="Risk",
                        y="Return",
                        text="Asset",
                        size=np.repeat(18, len(labels)),
                        title="Risk vs Return of Individual Assets"
                    )

                fig.update_traces(textposition="top center")

                fig.add_trace(
                        go.Scatter(
                            x=[portfolio_risk],
                            y=[portfolio_return],
                            mode="markers+text",
                            text=["Quantum Portfolio"],
                            marker=dict(size=20, color="red"),
                            name="Optimized Portfolio"
                        )
                    )

                fig.update_layout(
                        xaxis_title="Risk (Volatility)",
                        yaxis_title="Expected Return",
                        template="plotly_white"
                    )

                st.plotly_chart(fig, use_container_width=True)
            with st.container():
                col1,col2=st.columns(2)
                with col1:
                    st.subheader("QAOA Ansatz")
                    img = Image.open("img/qaoa_circuit.png")
                    img = img.resize((600, 600))
                    st.image(img)
                with col2:
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=sharpe_ratio,
                        number={"valueformat": ".3f"},
                        title={"text": "Quantum Portfolio Sharpe Ratio"},
                        gauge={
                            "axis": {"range": [-1, 3]},
                            "bar": {"color": "royalblue"},
                            "steps": [
                                {"range": [-1, 0], "color": "#ff4d4d"},
                                {"range": [0, 1], "color": "#ffd54f"},
                                {"range": [1, 2], "color": "#90ee90"},
                                {"range": [2, 3], "color": "#00c853"},
                            ]
                        }
                    ))

                    fig.update_layout(height=400)

                    st.plotly_chart(fig, use_container_width=True)
            with st.container():
                variables = qubo.variables
                n = len(variables)

                Q = np.zeros((n, n))

                objective = qubo.objective

                for idx, coeff in objective.linear.to_dict().items():
                    Q[idx, idx] = coeff

                for (i, j), coeff in objective.quadratic.to_dict().items():
                    Q[i, j] += coeff
                    if i != j:
                        Q[j, i] += coeff

                labels = labels

                fig = go.Figure(
                    data=go.Heatmap(
                        z=Q,
                        x=labels,
                        y=labels,
                        colorscale = [
                            [0.00, "#440154"],
                            [0.25, "#3b528b"],
                            [0.50, "#21918c"],
                            [0.75, "#5ec962"],
                            [1.00, "#fde725"]
                        ],
                        zmid=0,
                        text=np.round(Q, 2),
                        texttemplate="%{text}",
                        textfont={"size": 12},
                        hovertemplate=(
                            "<b>%{y}</b> ↔ <b>%{x}</b><br>"
                            "Coefficient: %{z:.4f}<extra></extra>"
                        ),
                        colorbar=dict(title="Coefficient")
                    )
                )

                fig.update_layout(
                    title="QUBO Matrix Heatmap",
                    xaxis_title="Binary Variables",
                    yaxis_title="Binary Variables",
                    width=750,
                    height=650,
                    template="plotly_white"
                )

                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.exception(e)

def classicalvsquantum():
    scroll_to_top()
    if "portfolio_data" not in st.session_state:
        st.warning("Please run portfolio optimization first.")
        return
    
    data = st.session_state["portfolio_data"]
    
    expected_returns = data["expected_returns"]
    covariance_matrix = data["covariance_matrix"]
    labels = data["labels"]
    daily_returns = data["daily_returns"]
    raw_data = data["raw_data"]
    tickers = data["tickers"]

    with st.container():
        st.header("🤝 Classical vs Quantum Portfolio Comparison",text_alignment="center")
        left,right=st.columns(2)
        with left:
            st.subheader("Classical Portfolio",text_alignment="center")
            try:
                with open("json/optimization_results.json", "r") as f:
                    saved_results = json.load(f)
                p_return = saved_results["portfolio_return"]
                p_volatility = saved_results["portfolio_volatility"]
                investment_values=saved_results["investment_values"]
                capital=saved_results["capital"]
                weights=saved_results["weights"]
                asset_profit=saved_results["assets_profit"]
                bin_opt=saved_results["bin_opt"]
                class_opt=saved_results["class_opt"]
                risk_free_rate = 0.05
                sharpe_ratio = (p_return - risk_free_rate) / p_volatility
                expected_profit=capital*p_return
                classical_transaction_cost=saved_results["total_transaction_cost"]
                classical_execution_time=saved_results["execution_time"]
                weight_series = (
                                pd.Series(weights)
                                .reindex(daily_returns.columns, fill_value=0)
                            )
                
                portfolio_daily_returns = (
                                daily_returns.mul(weight_series, axis=1)
                            ).sum(axis=1)
                
                confidence = 0.95
                
                classical_var = -np.percentile(portfolio_daily_returns,
                                                        (1-confidence)*100)
                
                classical_tail = portfolio_daily_returns[portfolio_daily_returns <= -classical_var]
                
                classical_cvar = -classical_tail.mean()
                with st.container():
                    with st.container():
                        col1,col2=st.columns(2)
                        with col1:
                            kpi_card(

                                "📈 Portfolio Return",
                                f"{p_return:.5f}",
                                "#2563EB" 
                            )
                        with col2:
                            kpi_card(

                                "📉 Portfolio Risk",
                                f"{p_volatility:.3f}",
                                "#DC2626"
                            )
                    with st.container():
                        col1,col2=st.columns(2)
                        with col1:
                            kpi_card(
    
                                "⚙️ Algorithm Used",
                                bin_opt,
                                "#7C3AED"      # Purple
                            )
                        with col2:
                            kpi_card(
    
                                "🧮 Classical Optimizer",
                                class_opt,
                                "#6366F1"      # Indigo
                            )
                    with st.container():
                        col1,col2=st.columns(2)
                        with col1:
                            kpi_card(
                                "⭐ Sharpe Ratio",
                                f"{sharpe_ratio:.5f}",
                                "#16A34A"      # Green
                            )
                        with col2:
                            kpi_card(
                                "💵 Expected Profit",
                                f"₹{expected_profit:,.2f}",
                                "#10B981"      # Emerald
                            )
                    with st.container():
                        invest_weights=pd.DataFrame(list(investment_values.items()),columns=["Ticker","Investment"])
                        fig = px.pie(
                        invest_weights,
                        names="Ticker",
                        values="Investment",
                        title="Portfolio Allocation",
                        )
                        
                        fig.update_layout(
                            width=300,
                            height=400
                        )
                        
                        st.plotly_chart(fig,use_container_width=True,key="classical_pie")                        
            except Exception as e:
                st.exception(e)
        with right:
            st.subheader("Quantum Portfolio",text_alignment="center")
            try:
                with open("json/quantum_optimization_results.json","r") as f:
                    result=json.load(f)
                                   
                
                portfolio_return=result["quantum_portfolio_return"]
                portfolio_risk=result["quantum_portfolio_risk"]
                portfolio_profit=result["quantum_expected_profit"]
                portfolio_weights_dict=result["optimized_weights"]
                quantum_transaction_cost=result["total_transaction_cost"]
                capital=result["capital"]
                algorithm=result["algo"]
                optimizer=result["optimizer"]
                circuit_layers=result["opt_layers"]
                circuit_depth=result["cir_depth"]
                risk_free_rate = 0.05
                sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_risk
                expected_profit = capital * portfolio_return
                normal_weights=result["normal_weights"]
                quantum_execution_time=result["execution_time"]
                investment_per_asset=result["investment_per_asset"]
                
                weights = (pd.Series(normal_weights).reindex(daily_returns.columns, fill_value=0))
                
                portfolio_daily_returns = (daily_returns.mul(weights, axis=1)).sum(axis=1)
                
                confidence=0.95
                quantum_var = -np.percentile(portfolio_daily_returns,(1-confidence)*100)
                
                quantum_tail = portfolio_daily_returns[portfolio_daily_returns <= -quantum_var]
                
                quantum_cvar = -quantum_tail.mean()
                with st.container():
                    with st.container():
                        col1,col2=st.columns(2)
                        with col1:
                            kpi_card(
                                "📈 Portfolio Return",
                                f"{portfolio_return:.5f}",
                                "#2563EB" 
                            )
                        with col2:
                            kpi_card(
                                "📉 Portfolio Risk",
                                f"{portfolio_risk:.3f}",
                                "#DC2626"
                            )
                    with st.container():
                        col1,col2=st.columns(2)
                        with col1:
                            kpi_card(
    
                                "⚙️ Algorithm Used",
                                algorithm,
                                "#7C3AED"      # Purple
                            )
                        with col2:
                            kpi_card(
    
                                "🧮 Classical Optimizer",
                                "SLSQP",
                                "#6366F1"      # Indigo
                            )
                    with st.container():
                        col1,col2=st.columns(2)
                        with col1:
                            kpi_card(
                                "⭐ Sharpe Ratio",
                                f"{sharpe_ratio:.5f}",
                                "#16A34A"      # Green
                            )
                        with col2:
                            kpi_card(
                                "💵 Expected Profit",
                                f"₹{expected_profit:,.2f}",
                                "#10B981"      # Emerald
                            )
                with st.container():
                    portfolio_df = pd.DataFrame(
                        list(investment_per_asset.items()),
                        columns=["Ticker", "Investment"]
                    )

                    fig = px.pie(
                        portfolio_df,
                        names="Ticker",
                        values="Investment",
                        title="Portfolio Allocation"
                    )

                    st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.exception(e)       

        
        classical_weights = (
            pd.Series(weights)
            .reindex(daily_returns.columns, fill_value=0)
        )

        classical_daily_returns = (
            daily_returns.mul(classical_weights, axis=1)
        ).sum(axis=1)

        confidence = 0.95

        classical_var = -np.percentile(classical_daily_returns, 5)
        classical_cvar = -classical_daily_returns[
            classical_daily_returns <= -classical_var
        ].mean()


        # Quantum
        quantum_weights = (
            pd.Series(normal_weights)
            .reindex(daily_returns.columns, fill_value=0)
        )

        quantum_daily_returns = (
            daily_returns.mul(quantum_weights, axis=1)
        ).sum(axis=1)

        quantum_var = -np.percentile(quantum_daily_returns, 5)
        quantum_cvar = -quantum_daily_returns[
            quantum_daily_returns <= -quantum_var
        ].mean()
        classical_sharpe = (p_return - risk_free_rate) / p_volatility
        quantum_sharpe = (portfolio_return - risk_free_rate) / portfolio_risk


        classical_profit = capital * p_return
        quantum_profit = capital * portfolio_return

        comparison_df = pd.DataFrame({
            "Metric": [
                "Return",
                "Risk",
                "Sharpe Ratio",
                "Expected Profit"
            ],
            "Classical": [
                p_return,
                p_volatility,
                classical_sharpe,
                classical_profit
            ],
            "Quantum": [
                portfolio_return,
                portfolio_risk,
                quantum_sharpe,
                quantum_profit
            ]
        })

        fig = px.bar(
            comparison_df,
            x="Metric",
            y=["Classical", "Quantum"],
            barmode="group",
            title="Classical vs Quantum Portfolio Performance",
            text_auto=".3f"
        )

        fig.update_layout(
            xaxis_title="Metrics",
            yaxis_title="Value",
            legend_title="Method",
            height=500
        )

        st.plotly_chart(fig, use_container_width=True)


    with st.container():
        col1,col2=st.columns(2)
        with col1:
            scatter_df = pd.DataFrame({
                "Method": ["Classical", "Quantum"],
                "Risk": [p_volatility, portfolio_risk],
                "Return": [p_return, portfolio_return]
            })

            fig = px.scatter(
                scatter_df,
                x="Risk",
                y="Return",
                color="Method",
                text="Method",
                size=[30, 30],
                title="Risk vs Return Comparison"
            )

            fig.update_traces(
                textposition="top center",
                marker=dict(size=22)
            )

            fig.update_layout(
                xaxis_title="Risk (Volatility)",
                yaxis_title="Expected Return",
                height=500
            )

            st.plotly_chart(fig, use_container_width=True)
        with col2:
            classical_df = pd.DataFrame(
                    list(investment_values.items()),
                    columns=["Ticker", "Classical"]
                    )
            
            quantum_df = pd.DataFrame(
                    list(investment_per_asset.items()),
                    columns=["Ticker", "Quantum"]
                    )
                
            allocation_df = pd.merge(
                        classical_df,
                        quantum_df,
                        on="Ticker",
                        how="outer"
                        ).fillna(0)
            
            fig = px.bar(
                        allocation_df,
                        x="Ticker",
                        y=["Classical", "Quantum"],
                        barmode="group",
                        title="Portfolio Allocation Comparison",
                        text_auto=".2f"
                        )
            
            fig.update_layout(
                        xaxis_title="Assets",
                        yaxis_title="Investment (₹)",
                        legend_title="Method",
                        height=500
                        )
            
            st.plotly_chart(fig, use_container_width=True)
    with st.container():
        col1,col2=st.columns(2)
        with col1:
            comparison_return = pd.DataFrame({
                "Method": ["Classical", "Quantum"],
                "Return": [p_return, portfolio_return]
            })

            fig = px.bar(
                comparison_return,
                x="Method",
                y="Return",
                color="Method",
                text_auto=".2%",
                title="Expected Portfolio Return Comparison"
            )

            st.plotly_chart(fig, use_container_width=True)
        with col2:
            comparison_risk = pd.DataFrame({
                "Method": ["Classical", "Quantum"],
                "Risk": [p_volatility, portfolio_risk]
            })

            fig = px.bar(
                comparison_risk,
                x="Method",
                y="Risk",
                color="Method",
                text_auto=".2%",
                title="Portfolio Risk Comparison"
            )

            st.plotly_chart(fig, use_container_width=True)
    with st.container():
        col1,col2=st.columns(2)
        with col1:
            comparison_var = pd.DataFrame({
                "Method": ["Classical", "Quantum"],
                "VaR": [classical_var, quantum_var]
            })

            fig = px.bar(
                comparison_var,
                x="Method",
                y="VaR",
                color="Method",
                text_auto=".4f",
                title="Value at Risk (95%)"
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            comparison_cvar = pd.DataFrame({
                "Method": ["Classical", "Quantum"],
                "CVaR": [classical_cvar, quantum_cvar]
            })

            fig = px.bar(
                comparison_cvar,
                x="Method",
                y="CVaR",
                color="Method",
                text_auto=".4f",
                title="Conditional Value at Risk (95%)"
            )

            st.plotly_chart(fig, use_container_width=True)
    with st.container():
        col1,col2=st.columns(2)
        with col1:
            comparison_sharpe = pd.DataFrame({
                "Method": ["Classical", "Quantum"],
                "Sharpe Ratio": [classical_sharpe, quantum_sharpe]
            })

            fig = px.bar(
                comparison_sharpe,
                x="Method",
                y="Sharpe Ratio",
                color="Method",
                text_auto=".6f",
                title="Sharpe Ratio Comparison"
            )

            st.plotly_chart(fig, use_container_width=True)
        with col2:
            comparison_time = pd.DataFrame({
                "Method": ["Classical", "Quantum"],
                "Execution Time (s)": [
                    classical_execution_time,
                    quantum_execution_time
                ]
            })

            fig = px.bar(
                comparison_time,
                x="Method",
                y="Execution Time (s)",
                color="Method",
                text_auto=".4f",
                title="Execution Time Comparison"
            )

            st.plotly_chart(fig, use_container_width=True)
    with st.container():
        st.header("🏆 Classical vs Quantum Winner")

        comparison = []
        comparison.append({
            "Metric": "Portfolio Return",
            "Classical": p_return,
            "Quantum": portfolio_return,
            "Winner": "Quantum" if portfolio_return > p_return else "Classical"
        })

        comparison.append({
            "Metric": "Expected Profit",
            "Classical": classical_profit,
            "Quantum": quantum_profit,
            "Winner": "Quantum" if quantum_profit > classical_profit else "Classical"
        })

        comparison.append({
            "Metric": "Sharpe Ratio",
            "Classical": classical_sharpe,
            "Quantum": quantum_sharpe,
            "Winner": "Quantum" if quantum_sharpe > classical_sharpe else "Classical"
        })

       
        comparison.append({
            "Metric": "Portfolio Risk",
            "Classical": p_volatility,
            "Quantum": portfolio_risk,
            "Winner": "Quantum" if portfolio_risk < p_volatility else "Classical"
        })

        comparison.append({
            "Metric": "VaR (95%)",
            "Classical": classical_var,
            "Quantum": quantum_var,
            "Winner": "Quantum" if quantum_var < classical_var else "Classical"
        })

        comparison.append({
            "Metric": "CVaR (95%)",
            "Classical": classical_cvar,
            "Quantum": quantum_cvar,
            "Winner": "Quantum" if quantum_cvar < classical_cvar else "Classical"
        })

        comparison.append({
            "Metric": "Transaction Cost",
            "Classical": classical_transaction_cost,
            "Quantum": quantum_transaction_cost,
            "Winner": "Quantum" if quantum_transaction_cost < classical_transaction_cost else "Classical"
        })

        comparison.append({
            "Metric": "Execution Time (s)",
            "Classical": classical_execution_time,
            "Quantum": quantum_execution_time,
            "Winner": "Quantum" if quantum_execution_time < classical_execution_time else "Classical"
        })

        comparison_df = pd.DataFrame(comparison)

        st.dataframe(comparison_df, use_container_width=True)

        classical_score = 0
        quantum_score = 0

        for row in comparison:
            if row["Winner"] == "Classical":
                classical_score += 1
            else:
                quantum_score += 1

        st.subheader("🥇 Overall Result")

        if quantum_score > classical_score:
            st.success(f"🚀 Quantum Portfolio Wins ({quantum_score} : {classical_score})")
        elif classical_score > quantum_score:
            st.success(f"📈 Classical Portfolio Wins ({classical_score} : {quantum_score})")
        else:
            st.info(f"🤝 Tie ({classical_score} : {quantum_score})")
        
def aicopilot():
    st.header("Welcome to MAPO Co-pilot",text_alignment="center")
    st.subheader("Ask Me Anything!....",text_alignment="center")
    ai_copilot()

if __name__=="__main__":
    with st.sidebar:
        st.sidebar.title("Portfolio Navigation")

        if "page" not in st.session_state:
            st.session_state.page = "Home"
        if st.sidebar.button("🏠 Home"):
            st.session_state.page="Home"
        if st.sidebar.button("⚙️ Portfolio Configuration"):
            st.session_state.page="Portfolio Configuration"
        if st.sidebar.button("📊 Financial Data"):
            st.session_state.page="Financial Data"
        if st.sidebar.button("💼 Classical Baseline"):
            st.session_state.page="Classical Baseline"
        if st.sidebar.button("⚛️ Quantum Portfolio"):
            st.session_state.page="Quantum Portfolio"
        if st.sidebar.button("⚖️ Classical Vs Quantum"):
            st.session_state.page="Classical vs Quantum"
        if st.sidebar.button("🎨 Portfolio Playground"):
            st.session_state.page="Portfolio Playground"
        if st.sidebar.button("🤖 AI Copilot"):
            st.session_state.page = "AI Copilot"



    if st.session_state.page=="Home":
        home_page()
    if st.session_state.page=="Portfolio Configuration":
        portfolio_configuration()
    if st.session_state.page=="Financial Data":
        details_of_the_assets()
    if st.session_state.page=="Classical Baseline":
        classical_baseline()
    if st.session_state.page=="Quantum Portfolio":
        quantum_portfolio_objectives()
    if st.session_state.page=="Classical vs Quantum":
        classicalvsquantum()
    if st.session_state.page=="Portfolio Playground":
        objective_playground()
    if st.session_state.page=="AI Copilot":
        aicopilot()

    

        

        

            
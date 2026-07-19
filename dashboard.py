import streamlit as st
from data import get_financial_data 
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

import json
st.set_page_config(layout="wide")
st.markdown(
    """
    <p style="margin:0; padding:0;">
       
    </p>
    """,
    unsafe_allow_html=True
)

def home_page():
    with st.container():
        st.title("Multi Asset Portfolio Optimization",text_alignment="center")
        
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
        

def details_of_the_assets(expected_returns,covariance_matrix,labels,daily_returns,raw_data):
    expected_returns_series = pd.Series(expected_returns, index=labels)
    
    mapping = {f"Asset {i+1}": ticker for i, ticker in enumerate(tickers)}
    expected_returns = expected_returns_series.rename(index=mapping)

    df_returns = expected_returns.to_frame(name="Expected Return")

    df_returns.index.name = "Ticker"

    with st.container():
        st.write("Expected Returns Analysis (Before Optimization)")

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
                st.write("Heat Map of Covariance Matrix")
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
                st.write("Correlation Matrix")

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
            st.write("Historical Price Trend")

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
            st.subheader("Efficient Frontier")

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
        with st.container():
            st.subheader("Cumulative Returns")

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
        with st.container():
            st.subheader("Risk vs Return")

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

def classical_baseline():
    with st.container():
        st.header("Classical Baseline Portfolio Objectives")
        try:
            with open("optimization_results.json", "r") as f:
                saved_results = json.load(f)
            
            
            weights_dict = saved_results["optimal_weights"]
            p_return = saved_results["portfolio_return"]
            p_volatility = saved_results["portfolio_volatility"]
            investment_values=saved_results["investment_values"]
            
            m_col1, m_col2,m_col3,m_col4 = st.columns(4)
            m_col1.metric("Optimized Expected Return", f"{round(p_return,2)}")
            m_col2.metric("Optimized Volatility", f"{round(p_volatility,3)}")
            
            # Format weights into a dataframe to display or chart
            df_weights = pd.DataFrame(list(weights_dict.items()), columns=["Ticker", "Optimal Weight"])
            st.subheader("Optimal Asset Weights")
            st.dataframe(df_weights, use_container_width=True)

            invest_weights=pd.DataFrame(list(investment_values.items()),columns=["Ticker","Investment"])
            fig = px.pie(
            invest_weights,
            names="Ticker",
            values="Investment",
            title="Portfolio Allocation"
            )

            st.plotly_chart(fig, use_container_width=True)
        except FileNotFoundError:
            st.error("Optimization file not found! Please run your backend script first to generate optimization_results.json.")

def quantum_portfolio_objectives():
    st.header("Quantum Processed Portfolio Objectives")
    with st.container():
        try:
            with open("quantum_optimization_results.json","r") as f:
                result=json.load(f)
               

            portfolio_return=result["quantum_portfolio_return"]
            portfolio_risk=result["quantum_portfolio_risk"]
            portfolio_profit=result["quantum_expected_profit"]
            portfolio_weights=result["optimized_weights"]
            col_1,col_2,col_3,col_4,col_5=st.columns(5)
            with col_1:
                col_1.metric("Portfolio Return",round(portfolio_return,3))
            with col_2:
                col_2.metric("Portfolio Risk",round(portfolio_risk,3))
            with col_3:
                col_3.metric("Expected Profit",portfolio_profit)
            with col_4:
                col_4.metric("Expected Risk",round(portfolio_risk*100000,3))
            with col_5:
                col_5.metric("Expected Day Profit",portfolio_profit//252)
                
            st.bar_chart(portfolio_weights)
        except:
            print("file not found")

if __name__=="__main__":
    tickers=["UVXY","WEAT","SQQQ","KOLD"]
    start_date="2025-06-01"
    end_date="2026-07-01"
    expected_returns,covariance_matrix,labels,daily_returns,raw_data=get_financial_data(tickers,start_date,end_date)

    
    with st.sidebar:
        st.write("Portfolio Navigation")

        if "page" not in st.session_state:
            st.session_state.page = "Home"
        if st.sidebar.button("🏠 Home"):
            st.session_state.page="Home"
        if st.sidebar.button("📊 Financial Data"):
            st.session_state.page="Financial Data"
        if st.sidebar.button("💼 Classical Baseline"):
            st.session_state.page="Classical Baseline"
        if st.sidebar.button("⚛️ Quantum Portfolio"):
            st.session_state.page="Quantum Portfolio"
            

    if st.session_state.page=="Home":
        home_page()
    if st.session_state.page=="Financial Data":
        details_of_the_assets(expected_returns,covariance_matrix,labels,daily_returns,raw_data)
    if st.session_state.page=="Classical Baseline":
        classical_baseline()
    if st.session_state.page=="Quantum Portfolio":
        quantum_portfolio_objectives()
        
        

            
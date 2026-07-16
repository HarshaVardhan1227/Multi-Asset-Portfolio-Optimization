import streamlit as st
from data import get_financial_data 
import pandas as pd

import json
with st.container():
    st.title("Hello Welcome to MAPO")
    st.write("Multi Asset Portfolio Optimization")


if __name__=="__main__":
    tickers=["UVXY","WEAT","SQQQ","KOLD"]
    start_date="2025-06-01"
    end_date="2026-07-01"
    expected_returns,covariance_matrix,labels=get_financial_data(tickers,start_date,end_date)

    
    expected_returns_series = pd.Series(expected_returns, index=labels)
    
    mapping = {f"Asset {i+1}": ticker for i, ticker in enumerate(tickers)}
    expected_returns = expected_returns_series.rename(index=mapping)

    df_returns = expected_returns.to_frame(name="Expected Return")

    df_returns.index.name = "Ticker"

    with st.container():
        st.header("Expected Returns Analysis (Before Optimization)")

        col1,col2=st.columns([1,2],gap='large')

        with col1:
            st.dataframe(df_returns,width=300)
        with col2:
            st.bar_chart(df_returns,width=500,height=300)
    with st.container():
        st.header("Classical Baseline Portfolio Objectives")
        try:
            with open("optimization_results.json", "r") as f:
                saved_results = json.load(f)
            
            
            weights_dict = saved_results["optimal_weights"]
            p_return = saved_results["portfolio_return"]
            p_volatility = saved_results["portfolio_volatility"]
            invest=saved_results["investment_values"]
            profit=saved_results["expected_profit"]
            risk=saved_results["expected_risk"]
 
            m_col1, m_col2,m_col3,m_col4 = st.columns(4)
            m_col1.metric("Optimized Expected Return", f"{round(p_return,2)}")
            m_col2.metric("Optimized Volatility", f"{round(p_volatility,3)}")
            m_col3.metric("Profit Margin",round(profit,3))
            m_col4.metric("Risk Margin",round(risk,4))
            st.bar_chart(invest)

            # Format weights into a dataframe to display or chart
            df_weights = pd.DataFrame(list(weights_dict.items()), columns=["Ticker", "Optimal Weight"])
            st.subheader("Optimal Asset Weights")
            st.dataframe(df_weights, use_container_width=True)
        except FileNotFoundError:
            st.error("Optimization file not found! Please run your backend script first to generate optimization_results.json.")

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
            
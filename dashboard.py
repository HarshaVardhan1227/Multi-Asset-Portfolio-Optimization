import streamlit as st
from data import get_financial_data 
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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
    st.header("Financial Data Analysis",text_alignment="center")
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

def classical_baseline(covariance_matrix,daily_returns):
    with st.container():
        st.header("Classical Baseline Portfolio Objectives",text_alignment="center")
        try:
            with open("optimization_results.json", "r") as f:
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
            
            m_col1, m_col2,m_col3,m_col4 = st.columns(4)
            m_col1.metric("Expected Return", f"{round(p_return,2)}")
            m_col2.metric("Expected Risk", f"{round(p_volatility,2)}")
            
            m_col3.metric("Capital",f"{capital}")

            m_col4.metric("Selected Assets","SPY")
            # Format weights into a dataframe to display or chart

            with st.container():
                col1,col2,col3,col4=st.columns(4,gap="small")

                with col1:
                    
                    col1.metric("Binary Optimizer",bin_opt)
                    
                with col2:
                    col2.metric("Classical Optimizer",class_opt)

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
                    num_portfolios = 5000
                    results = np.zeros((3, num_portfolios))

                    for i in range(num_portfolios):
                        w = np.random.random(len(tickers))
                        w /= np.sum(w)

                        portfolio_return = np.sum(expected_returns * w)
                        portfolio_risk = np.sqrt(np.dot(w.T, np.dot(covariance_matrix, w)))
                        sharpe = portfolio_return / portfolio_risk

                        results[0, i] = portfolio_risk
                        results[1, i] = portfolio_return
                        results[2, i] = sharpe

                    frontier_df = pd.DataFrame({
                        "Risk": results[0],
                        "Return": results[1],
                        "Sharpe": results[2]
                    })

                    fig = px.scatter(
                        frontier_df,
                        x="Risk",
                        y="Return",
                        color="Sharpe",
                        title="Efficient Frontier",
                        color_continuous_scale="Viridis"
                    )

                    fig.add_scatter(
                        x=[p_volatility],
                        y=[p_return],
                        mode="markers",
                        marker=dict(size=15, color="red", symbol="star"),
                        name="Optimal Portfolio"
                    )

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
        
def quantum_portfolio_objectives(covariance_matrix,daily_returns):
    st.header("Quantum Processed Portfolio Objectives",text_alignment="center")
    with st.container():
        try:
            with open("quantum_optimization_results.json","r") as f:
                result=json.load(f)
               
            capital=100000
            portfolio_return=result["quantum_portfolio_return"]
            portfolio_risk=result["quantum_portfolio_risk"]
            portfolio_profit=result["quantum_expected_profit"]
            portfolio_weights_dict=result["optimized_weights"]
            transaction_cost=result["total_transaction_cost"]
            algorithm=result["algo"]
            optimizer=result["optimizer"]
            circuit_layers=result["opt_layers"]
            circuit_depth=result["cir_depth"]
            risk_free_rate = 0.05
            sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_risk
            expected_profit = capital * portfolio_return

            
            col_1,col_2,col_3,col_4=st.columns(4)
            with col_1:
                col_1.metric("Portfolio Return",round(portfolio_return,3))
            with col_2:
                col_2.metric("Portfolio Risk",round(portfolio_risk,3))
            with col_3:
                col_3.metric("Expected Profit",int(portfolio_profit))
            with col_4:
                col_4.metric("Expected Risk",int(round(portfolio_risk*100000,3)))
            
            with st.container():
                col1,col2,col3,col4=st.columns(4,gap="large")
                with col1:
                    col1.metric("Alogrithm",algorithm)
                with col2:
                    col2.metric("Optimizer",optimizer)
                with col3:
                    col3.metric("Layers",circuit_layers)
                with col4:
                    col4.metric("Circuit Depth",circuit_depth)
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
        except Exception as e:
            st.exception(e)

def classicalvsquantum(covariance_matrix,daily_returns):
    with st.container():
        st.header("Comparision of Classical and Quantum Portfolio Optimizations",text_alignment="center")
        col1,col2=st.columns(2)
        with col1:
            st.subheader("Classical Objectives")
            try:
                with open("optimization_results.json", "r") as f:
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
                
                st.metric("Portfolio Return",round(p_return,5))
                st.metric("Portfolio Risk",round(p_volatility,3))
                st.metric("Algorithm Used",bin_opt)
                st.metric("Classical Optimizer",class_opt)
                st.metric("Sharpe Ratio",round(sharpe_ratio,5))
                st.metric("Expected Profit",round(expected_profit,3))
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
                    
                    st.plotly_chart(fig,use_container_width=True)                        
            except Exception as e:
                st.exception(e)
        with col2:
            st.subheader("Quantum Objectives")
            try:
                with open("quantum_optimization_results.json","r") as f:
                    result=json.load(f)
                                   
                capital=100000
                portfolio_return=result["quantum_portfolio_return"]
                portfolio_risk=result["quantum_portfolio_risk"]
                portfolio_profit=result["quantum_expected_profit"]
                portfolio_weights_dict=result["optimized_weights"]
                transaction_cost=result["total_transaction_cost"]
                algorithm=result["algo"]
                optimizer=result["optimizer"]
                circuit_layers=result["opt_layers"]
                circuit_depth=result["cir_depth"]
                risk_free_rate = 0.05
                sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_risk
                expected_profit = capital * portfolio_return

                
                st.metric("Portfolio Return",round(portfolio_return,5))
                st.metric("Portfolio Risk",round(portfolio_risk,3))
                st.metric("Algorithm Used",algorithm)
                st.metric("Classical Optimizer","SLSQP")
                st.metric("Sharpe Ratio",round(sharpe_ratio,5))
                st.metric("Expected Profit",round(expected_profit,3))
                with st.container():
                    portfolio_weights=pd.DataFrame(list(portfolio_weights_dict.items()),columns=["Ticker","Investment"])
                    fig = px.pie(
                    portfolio_weights,
                    names="Ticker",
                    values="Investment",
                    title="Portfolio Allocation",
                    )

                    fig.update_layout(
                    width=300,
                    height=400
                    )

                    st.plotly_chart(fig,use_container_width=True)
            except Exception as e:
                st.exception(e)       
        # Sharpe Ratios
        classical_sharpe = (p_return - risk_free_rate) / p_volatility
        quantum_sharpe = (portfolio_return - risk_free_rate) / portfolio_risk

        # Expected Profits
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

    

        classical_df = pd.DataFrame(
        list(investment_values.items()),
        columns=["Ticker", "Classical"]
        )

        quantum_df = pd.DataFrame(
        list(portfolio_weights_dict.items()),
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

if __name__=="__main__":
    tickers=["NVDA","AAPL","META","AMZN","MSFT","USO","SPY","KOLD"]
    start_date="2025-06-01"
    end_date="2026-07-01"
    expected_returns,covariance_matrix,labels,daily_returns,raw_data,liquidity_scores,transaction_cost_vector=get_financial_data(tickers,start_date,end_date)

    
    with st.sidebar:
        st.sidebar.title("Portfolio Navigation")

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
        if st.sidebar.button("Classical Vs Quantum"):
            st.session_state.page="Classical vs Quantum"

        st.sidebar.title("⚙️ Portfolio Configuration")
        st.sidebar.subheader("💰 Investment Settings")

        capital = st.sidebar.number_input(
            "Investment Capital (₹)",
            min_value=10000,
            max_value=100000000,
            value=100000,
            step=10000,
            help="Enter the total amount you wish to invest."
        )

        st.sidebar.subheader("📉 Risk Parameters")

        risk_aversion = st.sidebar.slider(
            "Risk Aversion (λ)",
            min_value=0.0,
            max_value=1.0,
            value=0.50,
            step=0.05,
            help="Higher values prioritize lower portfolio risk."
        )

        st.sidebar.subheader("💸 Transaction Settings")

        transaction_cost = st.sidebar.slider(
            "Transaction Cost (%)",
            min_value=0.0,
            max_value=2.0,
            value=0.10,
            step=0.05,
            help="Estimated trading cost percentage."
        ) / 100

        st.sidebar.subheader("📊 Portfolio Constraints")

        max_assets = st.sidebar.slider(
            "Maximum Assets",
            min_value=2,
            max_value=5,
            value=3
        )

        budget_constraint = st.sidebar.checkbox(
            "Enable Budget Constraint",
            value=True
        )

        diversification = st.sidebar.checkbox(
            "Enable Diversification Penalty",
            value=True
        )

        liquidity_constraint = st.sidebar.checkbox(
            "Enable Liquidity Constraint",
            value=True
        )
        run = st.sidebar.button(
            "🚀 Run Portfolio Optimization",
            use_container_width=True
        )
    if st.session_state.page=="Home":
        home_page()
    if st.session_state.page=="Financial Data":
        details_of_the_assets(expected_returns,covariance_matrix,labels,daily_returns,raw_data)
    if st.session_state.page=="Classical Baseline":
        classical_baseline(covariance_matrix,daily_returns)
    if st.session_state.page=="Quantum Portfolio":
        quantum_portfolio_objectives(covariance_matrix,daily_returns)
    if st.session_state.page=="Classical vs Quantum":
        classicalvsquantum(covariance_matrix,daily_returns)

    if run:
        st.success("Portfolio Optimization Started!")

        st.write("### Selected Parameters")

        st.write(f"**Investment Capital:** ₹{capital:,.2f}")
        st.write(f"**Risk Aversion:** {risk_aversion}")
        st.write(f"**Transaction Cost:** {transaction_cost:.2%}")
        
        

            
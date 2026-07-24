import yfinance as yf
import numpy as np
import pandas as pd
import os

assets = {
    "SPY": "US Equity",
    "EFA": "International Equity",
    "IEF": "Government Bond",
    "LQD": "Corporate Bond",
    "GLD": "Gold",
    "VNQ": "REIT",
    "SHV": "Cash"
}

def get_financial_data(tickers,start_date,end_date):
    raw_data=yf.download(tickers, start=start_date, end=end_date,auto_adjust=True)

    close_data = raw_data["Close"].ffill().bfill()

    volume_data = raw_data["Volume"].ffill().bfill()

    adj_close_data = raw_data['Close']


    adj_close_data = adj_close_data.ffill().bfill()
    
    daily_returns = adj_close_data.pct_change().dropna()


    dollar_volume = close_data * volume_data

    avg_dollar_volume = dollar_volume.mean()

    daily_mean = daily_returns.mean().values
    daily_cov = daily_returns.cov().values

    exp_returns=(daily_mean*252).round(5)

    cov_matrix=(daily_cov*252)

    anonymous_labels=list(tickers)

    log_liquidity = np.log1p(avg_dollar_volume)

    liquidity_scores = (
        (log_liquidity - log_liquidity.min()) /
        (log_liquidity.max() - log_liquidity.min())
    ).to_numpy()

    transaction_cost_vector = 1 / (liquidity_scores + 0.01)

    transaction_cost_vector /= transaction_cost_vector.max()
    return exp_returns,cov_matrix,anonymous_labels,daily_returns,adj_close_data,liquidity_scores,transaction_cost_vector


if __name__=="__main__":
    tickers=["NVDA","AAPL","META","AMZN","MSFT","USO","SPY","KOLD"]
    start_date="2025-06-01"
    end_date="2026-05-01"

    exp_returns,cov_matrix,labels,daily_returns,raw_data,liquidity_scores,transaction_cost_vector=get_financial_data(tickers,start_date,end_date)
    
    print(f"Expected Returns: {exp_returns}")

    cov_df=pd.DataFrame(cov_matrix, index=labels, columns=labels)
    print(f"Covariance DataFrame:\n{cov_df.round(6)}")

    print(type(liquidity_scores))
    print(transaction_cost_vector)
    print(type(transaction_cost_vector))
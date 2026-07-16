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
    raw_data=yf.download(tickers, start=start_date, end=end_date)

    if isinstance(raw_data.columns, pd.MultiIndex):
        adj_close_data = raw_data['Close'][tickers]
    else:
        adj_close_data = raw_data['Close']

    adj_close_data = adj_close_data.ffill().bfill()
    
    daily_returns = adj_close_data.pct_change().dropna()

    daily_mean = daily_returns.mean().values
    daily_cov = daily_returns.cov().values

    exp_returns=(daily_mean*252).round(5)

    cov_matrix=(daily_cov*252)

    anonymous_labels=[f"{ticker}" for i,ticker in enumerate((tickers))]

    return exp_returns,cov_matrix,anonymous_labels


if __name__=="__main__":
    tickers=["UVXY","WEAT","SQQQ","KOLD"]
    start_date="2025-06-01"
    end_date="2026-05-01"

    exp_returns,cov_matrix,labels=get_financial_data(tickers,start_date,end_date)
    
    print(f"Expected Returns: {exp_returns}")

    cov_df=pd.DataFrame(cov_matrix, index=labels, columns=labels)
    print(f"Covariance DataFrame:\n{cov_df.round(6)}")
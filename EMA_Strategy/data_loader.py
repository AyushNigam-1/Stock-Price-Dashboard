import yfinance as yf
import pandas as pd
import os
from datetime import datetime, timedelta

def get_data(ticker, period="60d", interval="15m", cache=True):
    cache_file = f"cache_{ticker}_{period}_{interval}.csv"
    
    if cache and os.path.exists(cache_file):
        mod_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
        if datetime.now() - mod_time < timedelta(hours=12):
            return pd.read_csv(cache_file, parse_dates=True, index_col=0)
    
    df = yf.download(ticker, period=period, interval=interval)
    if df.empty:
        raise Exception("Data fetch failed")
    df.to_csv(cache_file)
    return df

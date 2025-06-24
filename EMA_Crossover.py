import streamlit as st
import yfinance as yf
import pandas as pd
import os
from datetime import datetime, timedelta
import ta
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("📈 Intraday EMA Crossover Strategy Simulator")

# Function to fetch and cache intraday data
def get_intraday_data(ticker, period="5d", interval="5m", cache_dir="intraday_cache"):
    os.makedirs(cache_dir, exist_ok=True)
    filename = f"{ticker}_{period}_{interval}.csv"
    filepath = os.path.join(cache_dir, filename)

    if os.path.exists(filepath):
        mod_time = datetime.fromtimestamp(os.path.getmtime(filepath))
        if datetime.now() - mod_time < timedelta(hours=24):
            st.info(f"📁 Loaded cached data from: {filepath}")
            return pd.read_csv(filepath, index_col=0, parse_dates=True)
        else:
            os.remove(filepath)

    st.info(f"🌐 Downloading fresh data for {ticker}...")
    df = yf.download(ticker, period=period, interval=interval)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.to_csv(filepath)
    return df

# EMA Backtest using TA-Lib
def backtest_ema_strategy(df, short_ema, long_ema, initial_cash=100000):
    indicator_df = df.copy()
    indicator_df["EMA_SHORT"] = ta.trend.ema_indicator(indicator_df["Close"], window=short_ema)
    indicator_df["EMA_LONG"] = ta.trend.ema_indicator(indicator_df["Close"], window=long_ema)

    position = None
    signals = []
    trades = []
    correct_predictions = 0
    total_return = 0.0
    total_trades = 0
    balance = initial_cash

    prices = indicator_df["Close"].tolist()

    for i in range(1, len(prices)):
        ema_s, ema_l = indicator_df["EMA_SHORT"].iloc[i], indicator_df["EMA_LONG"].iloc[i]
        prev_ema_s, prev_ema_l = indicator_df["EMA_SHORT"].iloc[i-1], indicator_df["EMA_LONG"].iloc[i-1]

        if pd.isna(ema_s) or pd.isna(ema_l) or pd.isna(prev_ema_s) or pd.isna(prev_ema_l):
            signals.append(None)
            continue

        signal = None
        if prev_ema_s < prev_ema_l and ema_s > ema_l:
            signal = "buy"
        elif prev_ema_s > prev_ema_l and ema_s < ema_l:
            signal = "sell"

        signals.append(signal)

        if position is None and signal in ["buy", "sell"]:
            position = (signal, i)
        elif position and (
            (position[0] == 'buy' and signal == "sell") or
            (position[0] == 'sell' and signal == "buy")
        ):
            entry_type, entry_idx = position
            entry_price = prices[entry_idx]
            exit_price = prices[i]
            pnl = (exit_price - entry_price) if entry_type == 'buy' else (entry_price - exit_price)
            pct = pnl / entry_price * 100

            trades.append({
                "type": entry_type,
                "entry_time": indicator_df.index[entry_idx],
                "exit_time": indicator_df.index[i],
                "entry_price": entry_price,
                "exit_price": exit_price,
                "pnl": round(pnl, 2),
                "pct": round(pct, 2)
            })

            if (entry_type == 'buy' and exit_price > entry_price) or (entry_type == 'sell' and exit_price < entry_price):
                correct_predictions += 1

            total_return += pct
            total_trades += 1
            position = (signal, i)

        else:
            continue

    accuracy = (correct_predictions / total_trades) * 100 if total_trades > 0 else 0
    return signals, accuracy, total_trades, total_return, trades


# Optimizer using TA-Lib
def full_optimizer(ticker, intervals=["1m","5m","15m"], periods=["5d", "10d", "15d"], short_range=(5, 20), long_range=(21, 50)):
    best_config = {
        "accuracy": 0,
        "total_return": -999,
        "score": -999,
        "period": None,
        "short": None,
        "long": None,
        "interval": None
    }

    for interval in intervals:
        for period in periods:
            try:
                df = get_intraday_data(ticker, period=period, interval=interval)
                for short in range(short_range[0], short_range[1]):
                    for long in range(long_range[0], long_range[1]):
                        if short >= long:
                            continue
                        _, acc, _, ret,_ = backtest_ema_strategy(df, short, long)
                        score = acc + ret  # Weighted logic if needed

                        if score > best_config["score"]:
                            best_config.update({
                                "accuracy": acc,
                                "total_return": ret,
                                "short": short,
                                "long": long,
                                "period": period,
                                "interval": interval,
                                "score": score
                            })
            except Exception as e:
                print(f"Skipping {period}-{interval}: {e}")

    return best_config



# UI Input
ticker = st.text_input("Enter Stock Ticker", "AAPL")
period = st.selectbox("Select Period", ["5d", "10d", "15d"])
interval = st.selectbox("Select Interval", ["1m", "5m", "15m"])
ema_short = st.slider("Short EMA Window", 5, 20, 9)
ema_long = st.slider("Long EMA Window", 10, 50, 21)

# Run simulation
if st.button("🚀 Run EMA Crossover Simulation"):
    df = get_intraday_data(ticker, period=period, interval=interval)
    signals, acc, trades, total_ret, trade_log = backtest_ema_strategy(df, ema_short, ema_long)

    st.success(f"✅ Trades: {trades}")
    st.info(f"🎯 Accuracy: {acc:.2f}%")
    st.metric("📈 Total Return", f"{total_ret:.2f}%")
    st.metric("💰 Final Cash (Fake ₹100K Start)", f"₹{100000 * (1 + total_ret / 100):,.2f}")

    # Chart with buy/sell markers
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["Close"], name="Price", line=dict(color="blue")))
    fig.add_trace(go.Scatter(x=df.index, y=ta.trend.ema_indicator(df["Close"], ema_short), name=f"EMA {ema_short}", line=dict(color="green", dash="dot")))
    fig.add_trace(go.Scatter(x=df.index, y=ta.trend.ema_indicator(df["Close"], ema_long), name=f"EMA {ema_long}", line=dict(color="red", dash="dot")))

    for trade in trade_log:
        fig.add_trace(go.Scatter(
            x=[trade["entry_time"]],
            y=[trade["entry_price"]],
            mode="markers+text",
            name=f"{trade['type'].capitalize()} Entry",
            marker_symbol="triangle-up" if trade["type"] == "buy" else "triangle-down",
            marker_color="green" if trade["type"] == "buy" else "red",
            marker_size=12,
            text=["Buy" if trade["type"] == "buy" else "Sell"],
            textposition="top center"
        ))
        fig.add_trace(go.Scatter(
            x=[trade["exit_time"]],
            y=[trade["exit_price"]],
            mode="markers",
            name="Exit",
            marker_symbol="circle",
            marker_color="orange",
            marker_size=10
        ))

    fig.update_layout(title="📊 EMA Crossover Trade Chart", xaxis_title="Time", yaxis_title="Price", legend_title="Legend")
    st.plotly_chart(fig, use_container_width=True)

    # Trade log table
    st.subheader("📋 Trade Log")
    st.dataframe(pd.DataFrame(trade_log))

# Run optimizer
if st.button("🔍 Full Optimize (EMA + Period)"):
    result = full_optimizer(ticker)
    if result["short"] is not None:
        st.success("🚀 Best EMA + Period Found!")
        st.write(result)
    else:
        st.warning("No profitable configuration found.")

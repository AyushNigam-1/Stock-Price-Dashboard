import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

def simple_moving_average(prices, window):
    print(prices,window)
    sma = []
    for i in range(len(prices)):
        if i + 1 < window:
            sma.append(None)
        else:
            avg = sum(prices[i+1-window:i+1]) / window
            sma.append(avg)
    return sma

def exponential_moving_average(prices, window):
    ema = []
    alpha = 2 / (window + 1)
    for i in range(len(prices)):
        if i == 0:
            ema.append(prices[0])
        else:
            ema.append(alpha * prices[i] + (1 - alpha) * ema[-1])
    return ema

def rsi(prices, window):
    gains, losses = [0], [0]
    for i in range(1, len(prices)):
        change = prices[i] - prices[i-1]
        gains.append(max(change, 0))
        losses.append(abs(min(change, 0)))

    avg_gain, avg_loss = [], []
    for i in range(len(prices)):
        if i < window:
            avg_gain.append(None)
            avg_loss.append(None)
        else:
            avg_gain.append(sum(gains[i-window+1:i+1]) / window)
            avg_loss.append(sum(losses[i-window+1:i+1]) / window)

    rsi_values = []
    for g, l in zip(avg_gain, avg_loss):
        if g is None or l is None:
            rsi_values.append(None)
        elif l == 0:
            rsi_values.append(100)
        else:
            rs = g / l
            rsi_values.append(100 - (100 / (1 + rs)))
    return rsi_values

def macd(prices, short=12, long=26, signal=9):
    ema_short = exponential_moving_average(prices, short)
    ema_long = exponential_moving_average(prices, long)
    macd_line = [s - l if s is not None and l is not None else None for s, l in zip(ema_short, ema_long)]
    signal_line = exponential_moving_average([m if m is not None else 0 for m in macd_line], signal)
    return macd_line, signal_line

def bollinger_bands(prices, window, num_std):
    sma = simple_moving_average(prices, window)
    upper_band, lower_band = [], []
    for i in range(len(prices)):
        if i + 1 < window:
            upper_band.append(None)
            lower_band.append(None)
        else:
            window_data = prices[i+1-window:i+1]
            mean = sma[i]
            std = pd.Series(window_data).std()
            upper_band.append(mean + num_std * std)
            lower_band.append(mean - num_std * std)
    return upper_band, lower_band

st.set_page_config(layout="wide")
st.title("📈 Live Stock Price Dashboard")

ticker = st.text_input("Enter Stock Ticker (e.g., AAPL, TCS.NS)", "AAPL")
stock = yf.Ticker(ticker)

days = st.slider("Select number of days", 30, 365, 90)
df = stock.history(period=f"{days}d").reset_index()

close_prices = df["Close"].tolist()

# Moving Averages
ma1 = st.slider("MA1 window", 5, 100, 20)
ma2 = st.slider("MA2 window", 5, 200, 50)
df["SMA1"] = simple_moving_average(close_prices, ma1)
df["SMA2"] = simple_moving_average(close_prices, ma2)
df["EMA1"] = exponential_moving_average(close_prices, ma1)
df["EMA2"] = exponential_moving_average(close_prices, ma2)

# RSI
df["RSI"] = rsi(close_prices, 14)

# MACD
macd_line, signal_line = macd(close_prices)
df["MACD"] = macd_line
df["Signal_Line"] = signal_line

# Bollinger Bands
upper_band, lower_band = bollinger_bands(close_prices, 20, 2)
df["BB_Upper"] = upper_band
df["BB_Lower"] = lower_band

# Plotting
fig = go.Figure()
fig.add_trace(go.Scatter(x=df["Date"], y=df["Close"], name="Close Price"))
fig.update_layout(title=f"{ticker} Close Price - Last {days} Days", xaxis_title="Date", yaxis_title="Price")
st.plotly_chart(fig, use_container_width=True)

fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=df["Date"], y=df["Close"], name="Close"))
fig2.add_trace(go.Scatter(x=df["Date"], y=df["SMA1"], name=f"SMA{ma1}"))
fig2.add_trace(go.Scatter(x=df["Date"], y=df["EMA1"], name=f"EMA{ma1}"))
fig2.add_trace(go.Scatter(x=df["Date"], y=df["SMA2"], name=f"SMA{ma2}"))
fig2.add_trace(go.Scatter(x=df["Date"], y=df["EMA2"], name=f"EMA{ma2}"))
fig2.update_layout(title="Moving Averages", xaxis_title="Date", yaxis_title="Price")
st.plotly_chart(fig2, use_container_width=True)

fig3 = go.Figure()
fig3.add_trace(go.Scatter(x=df["Date"], y=df["RSI"], name="RSI"))
fig3.add_hline(y=70, line_dash="dash", line_color="red")
fig3.add_hline(y=30, line_dash="dash", line_color="green")
fig3.update_layout(title="RSI (14)", xaxis_title="Date", yaxis_title="RSI")
st.plotly_chart(fig3, use_container_width=True)

fig4 = go.Figure()
fig4.add_trace(go.Scatter(x=df["Date"], y=df["MACD"], name="MACD"))
fig4.add_trace(go.Scatter(x=df["Date"], y=df["Signal_Line"], name="Signal Line"))
fig4.update_layout(title="MACD", xaxis_title="Date", yaxis_title="Value")
st.plotly_chart(fig4, use_container_width=True)

fig5 = go.Figure()
fig5.add_trace(go.Scatter(x=df["Date"], y=df["Close"], name="Close"))
fig5.add_trace(go.Scatter(x=df["Date"], y=df["BB_Upper"], name="Upper Band"))
fig5.add_trace(go.Scatter(x=df["Date"], y=df["BB_Lower"], name="Lower Band"))
fig5.update_layout(title="Bollinger Bands (20, 2)", xaxis_title="Date", yaxis_title="Price")
st.plotly_chart(fig5, use_container_width=True)

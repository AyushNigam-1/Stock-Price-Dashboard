import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands

st.set_page_config(layout="wide")
st.title("📈 Live Stock Price Dashboard")

ticker = st.text_input("Enter Stock Ticker (e.g., AAPL, TCS.NS)", "AAPL")

stock = yf.Ticker(ticker)

# col1, col2 = st.columns(2)

# with col1:
st.subheader("📅 Historical Price")
days = st.slider("Select number of days", 30, 365, 90)
df = stock.history(period=f"{days}d")
print(df)
df = df.reset_index()

fig = go.Figure()
fig.add_trace(go.Scatter(x=df["Date"], y=df["Close"], name="Close Price"))
fig.update_layout(title=f"{ticker} Close Price - Last {days} Days", xaxis_title="Date", yaxis_title="Price")
st.plotly_chart(fig, use_container_width=True)

# with col2:
st.subheader("📊 Moving Averages")
ma1 = st.slider("MA1 window", 5, 100, 20)
ma2 = st.slider("MA2 window", 5, 200, 50)
df["MA1"] = df["Close"].rolling(ma1).mean()
df["MA2"] = df["Close"].rolling(ma2).mean()

fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=df["Date"], y=df["Close"], name="Close"))
fig2.add_trace(go.Scatter(x=df["Date"], y=df["MA1"], name=f"MA{ma1}"))
fig2.add_trace(go.Scatter(x=df["Date"], y=df["MA2"], name=f"MA{ma2}"))
fig2.update_layout(title="Moving Averages", xaxis_title="Date", yaxis_title="Price")
st.plotly_chart(fig2, use_container_width=True)

df = df.reset_index()

# EMA (Exponential Moving Average)
ema_indicator = EMAIndicator(close=df["Close"], window=20)
df["EMA20"] = ema_indicator.ema_indicator()

# RSI (Relative Strength Index)
rsi_indicator = RSIIndicator(close=df["Close"], window=14)
df["RSI"] = rsi_indicator.rsi()

# MACD (Moving Average Convergence Divergence)
macd = MACD(close=df["Close"])
df["MACD"] = macd.macd()
df["Signal_Line"] = macd.macd_signal()

# Bollinger Bands
bb = BollingerBands(close=df["Close"], window=20, window_dev=2)
df["BB_Upper"] = bb.bollinger_hband()
df["BB_Lower"] = bb.bollinger_lband()

st.subheader("📈 EMA vs Close Price")
fig3 = go.Figure()
fig3.add_trace(go.Scatter(x=df["Date"], y=df["Close"], name="Close"))
fig3.add_trace(go.Scatter(x=df["Date"], y=df["EMA20"], name="EMA20"))
fig3.update_layout(title="Close Price with EMA", xaxis_title="Date", yaxis_title="Price")
st.plotly_chart(fig3, use_container_width=True)

st.subheader("📉 RSI Indicator")
fig4 = go.Figure()
fig4.add_trace(go.Scatter(x=df["Date"], y=df["RSI"], name="RSI"))
fig4.add_hline(y=70, line_dash="dash", line_color="red")
fig4.add_hline(y=30, line_dash="dash", line_color="green")
fig4.update_layout(title="RSI (14)", xaxis_title="Date", yaxis_title="RSI")
st.plotly_chart(fig4, use_container_width=True)

st.subheader("📉 MACD Indicator")
fig5 = go.Figure()
fig5.add_trace(go.Scatter(x=df["Date"], y=df["MACD"], name="MACD"))
fig5.add_trace(go.Scatter(x=df["Date"], y=df["Signal_Line"], name="Signal Line"))
fig5.update_layout(title="MACD", xaxis_title="Date", yaxis_title="Value")
st.plotly_chart(fig5, use_container_width=True)

st.subheader("📊 Bollinger Bands")
fig6 = go.Figure()
fig6.add_trace(go.Scatter(x=df["Date"], y=df["Close"], name="Close"))
fig6.add_trace(go.Scatter(x=df["Date"], y=df["BB_Upper"], name="Upper Band"))
fig6.add_trace(go.Scatter(x=df["Date"], y=df["BB_Lower"], name="Lower Band"))
fig6.update_layout(title="Bollinger Bands (20, 2)", xaxis_title="Date", yaxis_title="Price")
st.plotly_chart(fig6, use_container_width=True)

import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("📈 Advanced Stock Analysis Dashboard (TA-Lib Replacement with TA Library)")

# Input
ticker = st.text_input("Enter Stock Ticker (e.g., AAPL, TCS.NS)", "AAPL")
days = st.slider("Select number of days", 30, 365, 90)
window = st.slider("ATR & SD Window (in days)", 5, 50, 14)

# Download data
df = yf.download(ticker, period=f"{days}d")
if df.empty:
    st.error("❌ Could not fetch data. Please try another ticker or time range.")
    st.stop()

df.dropna(inplace=True)
if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)

# Initialize TA library
indicator_df = ta.utils.dropna(df.copy())

# SMA and EMA
ma1 = st.slider("MA1 window", 5, 100, 20)
ma2 = st.slider("MA2 window", 5, 200, 50)
indicator_df["SMA1"] = ta.trend.sma_indicator(indicator_df["Close"], window=ma1)
indicator_df["SMA2"] = ta.trend.sma_indicator(indicator_df["Close"], window=ma2)
indicator_df["EMA1"] = ta.trend.ema_indicator(indicator_df["Close"], window=ma1)
indicator_df["EMA2"] = ta.trend.ema_indicator(indicator_df["Close"], window=ma2)

# RSI
indicator_df["RSI"] = ta.momentum.rsi(indicator_df["Close"], window=14)

# MACD
macd = ta.trend.MACD(indicator_df["Close"], window_slow=26, window_fast=12)
indicator_df["MACD"] = macd.macd()
indicator_df["MACD_SIGNAL"] = macd.macd_signal()

# Bollinger Bands
bb = ta.volatility.BollingerBands(indicator_df["Close"], window=20, window_dev=2)
indicator_df["BB_UPPER"] = bb.bollinger_hband()
indicator_df["BB_LOWER"] = bb.bollinger_lband()

# ATR & Standard Deviation
indicator_df['ATR'] = ta.volatility.average_true_range(df['High'], df['Low'], df['Close'], window=window)
indicator_df['ATR_%'] = (indicator_df['ATR'] / df['Close']) * 100

indicator_df['SD'] = df['Close'].pct_change().rolling(window=window).std() * 100

# Latest values
st.subheader(f"📊 Standard Deviation & ATR (Window = {window} days)")
st.metric("📉 Standard Deviation (latest)", f"{indicator_df['SD'].iloc[-1]:.2f}%")
st.metric("📈 ATR (latest)", f"{indicator_df['ATR'].iloc[-1]:.2f} points")
st.metric("📈 ATR Percentage (latest)", f"{indicator_df['ATR_%'].iloc[-1]:.2f}%")

# Interpretation thresholds
def interpret_volatility(value, thresholds):
    if value < thresholds[0]: return "🟢 Low"
    elif value < thresholds[1]: return "🟡 Medium"
    else: return "🔴 High"

st.write("**Volatility Rating (Standard Deviation):**", interpret_volatility(indicator_df['SD'].iloc[-1], [1.0, 2.0]))
st.write("**ATR Rating:**", interpret_volatility(indicator_df['ATR_%'].iloc[-1], [1.5, 3.0]))

# Plots
fig_price = go.Figure()
fig_price.add_trace(go.Scatter(x=indicator_df.index, y=indicator_df['Close'], name="Close Price"))
fig_price.update_layout(title=f"{ticker} - Close Price", xaxis_title="Date", yaxis_title="Price")
st.plotly_chart(fig_price, use_container_width=True)

fig_ma = go.Figure()
fig_ma.add_trace(go.Scatter(x=indicator_df.index, y=indicator_df['SMA1'], name=f"SMA {ma1}"))
fig_ma.add_trace(go.Scatter(x=indicator_df.index, y=indicator_df['EMA1'], name=f"EMA {ma1}"))
fig_ma.add_trace(go.Scatter(x=indicator_df.index, y=indicator_df['SMA2'], name=f"SMA {ma2}"))
fig_ma.add_trace(go.Scatter(x=indicator_df.index, y=indicator_df['EMA2'], name=f"EMA {ma2}"))
fig_ma.update_layout(title="Moving Averages", xaxis_title="Date", yaxis_title="Price")
st.plotly_chart(fig_ma, use_container_width=True)

fig_rsi = go.Figure()
fig_rsi.add_trace(go.Scatter(x=indicator_df.index, y=indicator_df['RSI'], name="RSI"))
fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
fig_rsi.update_layout(title="RSI", xaxis_title="Date", yaxis_title="RSI")
st.plotly_chart(fig_rsi, use_container_width=True)

fig_macd = go.Figure()
fig_macd.add_trace(go.Scatter(x=indicator_df.index, y=indicator_df['MACD'], name="MACD"))
fig_macd.add_trace(go.Scatter(x=indicator_df.index, y=indicator_df['MACD_SIGNAL'], name="Signal"))
fig_macd.update_layout(title="MACD", xaxis_title="Date", yaxis_title="Value")
st.plotly_chart(fig_macd, use_container_width=True)

fig_bb = go.Figure()
fig_bb.add_trace(go.Scatter(x=indicator_df.index, y=indicator_df['Close'], name="Close"))
fig_bb.add_trace(go.Scatter(x=indicator_df.index, y=indicator_df['BB_UPPER'], name="Upper Band"))
fig_bb.add_trace(go.Scatter(x=indicator_df.index, y=indicator_df['BB_LOWER'], name="Lower Band"))
fig_bb.update_layout(title="Bollinger Bands", xaxis_title="Date", yaxis_title="Price")
st.plotly_chart(fig_bb, use_container_width=True)

fig_vol = go.Figure()
fig_vol.add_trace(go.Scatter(x=indicator_df.index, y=indicator_df['SD'], name="Standard Deviation (%)"))
fig_vol.add_trace(go.Scatter(x=indicator_df.index, y=indicator_df['ATR'], name="ATR (points)"))
fig_vol.update_layout(title="Volatility Indicators", xaxis_title="Date", yaxis_title="Volatility")
st.plotly_chart(fig_vol, use_container_width=True)

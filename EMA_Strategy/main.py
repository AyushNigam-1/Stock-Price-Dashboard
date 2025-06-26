import streamlit as st
from strategy import add_ema_signals, backtest_strategy
from plotter import plot_signals
import yfinance as yf

def main():
    st.set_page_config(layout="wide")
    st.title("📈 EMA Crossover Strategy Backtest")

    ticker = st.text_input("Enter Stock Ticker", "AAPL")
    short_ema = st.slider("Short EMA Period", 5, 50, 9)
    long_ema = st.slider("Long EMA Period", 10, 100, 21)

    if st.button("Run Strategy Backtest"):
        df = yf.download(ticker, period="15d", interval="15m")
        df = add_ema_signals(df, short_ema, long_ema)
        df, results = backtest_strategy(df)

        # ✅ Show Metrics
        st.subheader("📊 Strategy Performance")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Trades", results["trades"])
        col2.metric("Accuracy", f"{results['accuracy']:.2f}%")
        col3.metric("Total Return", f"{results['total_return']:.2f}%")
        col4.metric("Win Rate", f"{results['win_rate']:.2f}%")

        # ✅ Show Chart
        st.subheader("📉 Trade Signals Chart")
        plot_signals(df)

if __name__ == "__main__":
    main()

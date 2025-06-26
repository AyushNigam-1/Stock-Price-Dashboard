import matplotlib.pyplot as plt
import streamlit as st

def plot_signals(df):
    import matplotlib.pyplot as plt
    import streamlit as st

    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df["Close"], label="Close", alpha=0.5)
    plt.plot(df.index, df["EMA_SHORT"], label="EMA Short", linestyle="--")
    plt.plot(df.index, df["EMA_LONG"], label="EMA Long", linestyle="--")

    buys = df[df["Signal"] == 1]
    sells = df[df["Signal"] == -1]

    plt.scatter(buys.index, buys["Close"], marker="^", color="green", label="Buy", s=100)
    plt.scatter(sells.index, sells["Close"], marker="v", color="red", label="Sell", s=100)

    plt.title("EMA Crossover Signals")
    plt.xlabel("Time")
    plt.ylabel("Price")
    plt.legend()
    st.pyplot(plt.gcf())
    plt.clf()



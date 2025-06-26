def backtest(df, initial_capital=100000):
    df = df.copy()
    capital = initial_capital
    position = 0
    trade_log = []

    for i in range(1, len(df)):
        signal = df["Signal"].iloc[i]
        price = df["Close"].iloc[i]

        if signal == 1 and position == 0:
            position = capital / price
            capital = 0
            trade_log.append({"type": "BUY", "price": price, "time": df.index[i]})

        elif signal == -1 and position > 0:
            capital = position * price
            trade_log.append({"type": "SELL", "price": price, "time": df.index[i]})
            position = 0

    final_value = capital + (position * df["Close"].iloc[-1])
    return final_value, trade_log

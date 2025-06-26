import ta

def add_ema_signals(df, short_window, long_window):
    df = df.copy()
    df["EMA_SHORT"] = ta.trend.ema_indicator(df["Close"], window=short_window)
    df["EMA_LONG"] = ta.trend.ema_indicator(df["Close"], window=long_window)

    df["Signal"] = 0
    df.loc[(df["EMA_SHORT"] > df["EMA_LONG"]) & (df["EMA_SHORT"].shift() <= df["EMA_LONG"].shift()), "Signal"] = 1
    df.loc[(df["EMA_SHORT"] < df["EMA_LONG"]) & (df["EMA_SHORT"].shift() >= df["EMA_LONG"].shift()), "Signal"] = -1
    return df

def backtest_strategy(df):
    position = None
    entry_price = 0
    trades = 0
    correct = 0
    total_return = 0
    results = []

    for i in range(1, len(df)):
        signal = df["Signal"].iloc[i]

        if signal in [1, -1]:
            if position:
                exit_price = df["Close"].iloc[i]
                pnl = (exit_price - entry_price) / entry_price * 100 if position == "buy" else (entry_price - exit_price) / entry_price * 100
                if pnl > 0:
                    correct += 1
                total_return += pnl
                trades += 1
            position = "buy" if signal == 1 else "sell"
            entry_price = df["Close"].iloc[i]

    accuracy = (correct / trades * 100) if trades > 0 else 0
    win_rate = accuracy

    return df, {
        "accuracy": accuracy,
        "total_return": total_return,
        "trades": trades,
        "win_rate": win_rate
    }

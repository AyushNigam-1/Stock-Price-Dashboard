def evaluate(initial, final, trades):
    gain = final - initial
    return {
        "Initial Capital": initial,
        "Final Value": round(final, 2),
        "Net P/L": round(gain, 2),
        "Return (%)": round((gain / initial) * 100, 2),
        "Trades Executed": len(trades)
    }

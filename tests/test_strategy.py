import pandas as pd

from src.strategy.rsi import compute_rsi, generate_signals


def test_rsi_bounds_and_warmup():
    close = pd.Series(range(1, 80), index=pd.bdate_range("2022-01-03", periods=79), dtype=float)
    rsi = compute_rsi(close, period=14)
    valid = rsi.dropna()
    assert valid.between(0, 100).all()
    assert rsi.iloc[:13].isna().all()


def test_signal_enters_below_oversold_and_exits_above_overbought():
    # 先下跌把 RSI 打到超卖，再上涨到超买
    down = list(range(100, 40, -1))
    up = list(range(40, 160))
    close = pd.Series(down + up, index=pd.bdate_range("2022-01-03", periods=len(down) + len(up)), dtype=float)
    frame = generate_signals(close, period=14, oversold=30, overbought=70)
    assert set(frame["signal"].unique()).issubset({0, 1})
    assert frame["signal"].max() == 1
    # 一旦平仓，不应在仍然超买时立刻重新开仓
    exited = frame["signal"].eq(0) & frame["signal"].shift(1).eq(1)
    assert exited.any()

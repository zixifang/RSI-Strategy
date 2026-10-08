import pandas as pd

from src.backtest.engine import run_backtest
from src.backtest.metrics import cumulative_return, max_drawdown


def test_flat_signal_has_no_return():
    index = pd.bdate_range("2023-01-02", periods=5)
    close = pd.Series([10, 11, 12, 11, 13], index=index, dtype=float)
    signal = pd.Series(0, index=index)
    result = run_backtest(close, signal, fee=0.0)
    assert result.equity_curve.iloc[-1] == 1.0
    assert result.trades.empty
    assert cumulative_return(result.equity_curve) == 0.0


def test_buy_and_hold_matches_price_when_always_long_and_no_cost():
    index = pd.bdate_range("2023-01-02", periods=4)
    close = pd.Series([10.0, 10.0, 11.0, 12.1], index=index)
    # 第 0 日信号，第 1 日起持仓，因此用第 1 日收盘作为建仓价
    signal = pd.Series(1, index=index)
    result = run_backtest(close, signal, fee=0.0, slippage=0.0)
    expected = close.iloc[-1] / close.iloc[1] - 1
    assert abs(result.metrics["cumulative_return"] - expected) < 1e-12


def test_max_drawdown_is_negative_on_decline():
    equity = pd.Series([1.0, 1.2, 0.9, 1.0])
    assert max_drawdown(equity) == (0.9 / 1.2 - 1)

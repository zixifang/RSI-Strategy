"""RSI 均值回归策略。

规则（多头）：
- RSI 跌破 oversold 时开多
- RSI 升破 overbought 时平仓
- 信号在当日收盘确定，回测引擎会把仓位后移一天再计算收益，避免用到未来价格
"""

from __future__ import annotations

import numpy as np
import pandas as pd

DEFAULT_PERIOD = 14
DEFAULT_OVERSOLD = 30.0
DEFAULT_OVERBOUGHT = 70.0


def compute_rsi(close: pd.Series, period: int = DEFAULT_PERIOD) -> pd.Series:
    """Wilder RSI。前 period 根 K 线为 NaN。"""
    if period < 2:
        raise ValueError("period 必须 >= 2")
    delta = close.diff()
    gain = delta.clip(lower=0.0)
    loss = (-delta).clip(lower=0.0)
    avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0.0, np.nan)
    rsi = 100.0 - (100.0 / (1.0 + rs))
    return rsi.astype("float64")


def generate_signals(
    close: pd.Series,
    period: int = DEFAULT_PERIOD,
    oversold: float = DEFAULT_OVERSOLD,
    overbought: float = DEFAULT_OVERBOUGHT,
) -> pd.DataFrame:
    """由收盘价生成 RSI 与目标仓位。

    参数
    ----
    close :
        单标的收盘价，索引为日期，按时间升序。
    period, oversold, overbought :
        RSI 窗口与开平仓阈值。要求 oversold < overbought。

    返回
    ----
    DataFrame，索引与 close 相同，列：
    - close: float
    - rsi: float
    - signal: int，1 表示持有多头，0 表示空仓
    """
    if oversold >= overbought:
        raise ValueError("oversold 必须小于 overbought")
    if not isinstance(close, pd.Series):
        raise TypeError("close 必须是 pandas.Series")
    close = close.astype("float64").sort_index()

    rsi = compute_rsi(close, period)
    signal: list[int] = []
    holding = 0
    for value in rsi:
        if pd.isna(value):
            signal.append(0)
            continue
        if holding == 0 and value < oversold:
            holding = 1
        elif holding == 1 and value > overbought:
            holding = 0
        signal.append(holding)

    return pd.DataFrame(
        {"close": close.to_numpy(), "rsi": rsi.to_numpy(), "signal": signal},
        index=close.index,
    )

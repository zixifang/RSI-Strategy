"""回测指标。夏普使用日收益、无风险利率记为 0 的简化版。"""

from __future__ import annotations

import math

import pandas as pd

TRADING_DAYS = 252


def cumulative_return(equity: pd.Series) -> float:
    """累计收益率。equity 起点应为 1.0。"""
    if equity.empty:
        return 0.0
    return float(equity.iloc[-1] / equity.iloc[0] - 1.0)


def max_drawdown(equity: pd.Series) -> float:
    """最大回撤，返回负数或 0。例如 -0.2 表示回撤 20%。"""
    if equity.empty:
        return 0.0
    peak = equity.cummax()
    drawdown = equity / peak - 1.0
    return float(drawdown.min())


def sharpe_ratio(daily_returns: pd.Series, trading_days: int = TRADING_DAYS) -> float:
    """年化夏普比率。收益标准差为 0 时返回 0。"""
    returns = daily_returns.dropna()
    if len(returns) < 2:
        return 0.0
    std = float(returns.std(ddof=1))
    if std == 0.0 or math.isnan(std):
        return 0.0
    return float(returns.mean() / std * math.sqrt(trading_days))


def summarize(equity: pd.Series, daily_returns: pd.Series) -> dict[str, float]:
    return {
        "cumulative_return": cumulative_return(equity),
        "max_drawdown": max_drawdown(equity),
        "sharpe": sharpe_ratio(daily_returns),
    }

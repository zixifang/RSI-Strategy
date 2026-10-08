"""可视化接口。绘图由角色 C 实现，这里只固定函数签名和输入。

输入一律来自角色 A 的 BacktestResult，以及策略 DataFrame（含 close/rsi/signal）。
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.backtest.engine import BacktestResult


def plot_price_signals(
    strategy: pd.DataFrame,
    ticker: str,
    save_path: Path | None = None,
) -> None:
    """价格曲线，并在买入、卖出位置打点。strategy 需含 close、signal。"""
    _require_columns(strategy, ["close", "signal"])
    raise NotImplementedError("角色 C：绘制价格曲线与买卖点")


def plot_equity(
    result: BacktestResult,
    ticker: str,
    save_path: Path | None = None,
) -> None:
    """策略净值 vs 买入持有净值。"""
    raise NotImplementedError("角色 C：绘制收益曲线对比")


def plot_drawdown(
    result: BacktestResult,
    ticker: str,
    save_path: Path | None = None,
) -> None:
    """策略回撤曲线。"""
    raise NotImplementedError("角色 C：绘制回撤曲线")


def metrics_table(result: BacktestResult) -> pd.DataFrame:
    """把策略与基准指标排成表，供 PPT / JSON 使用。角色 C 可在此基础上导出。"""
    rows = {
        "strategy": result.metrics,
        "buy_and_hold": result.benchmark_metrics,
    }
    return pd.DataFrame(rows).T.rename_axis("book")


def _require_columns(frame: pd.DataFrame, columns: list[str]) -> None:
    missing = [col for col in columns if col not in frame.columns]
    if missing:
        raise ValueError(f"缺少列: {missing}")

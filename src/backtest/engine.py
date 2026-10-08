"""轻量日频回测。只做多、全仓进出，不引入 backtrader。"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from src.backtest.metrics import summarize


@dataclass
class BacktestResult:
    """角色 C 可视化与汇报表格都从这里取数。"""

    equity_curve: pd.Series
    benchmark_curve: pd.Series
    daily_returns: pd.Series
    positions: pd.Series
    trades: pd.DataFrame
    metrics: dict[str, float]
    benchmark_metrics: dict[str, float]


def run_backtest(
    close: pd.Series,
    signal: pd.Series,
    fee: float = 0.001,
    slippage: float = 0.0,
) -> BacktestResult:
    """按收盘价和目标仓位做日频回测。

    约定
    ----
    - signal 在 t 日收盘生成，仓位从 t+1 日收益开始生效（signal.shift(1)）。
    - 每次换仓按成交额扣除 fee + slippage。全仓进出时，换仓成本约为该比例。
    - 买入持有基准同样从第 2 个交易日起计算，和策略对齐。
    - close / signal 索引必须一致，且按日期升序。

    trades 列
    ---------
    date, side（buy/sell）, price, position_after
    """
    if fee < 0 or slippage < 0:
        raise ValueError("fee 与 slippage 不能为负")
    close = close.astype("float64").sort_index()
    signal = signal.reindex(close.index).fillna(0).astype(int)
    if not close.index.equals(signal.index):
        raise ValueError("signal 索引必须与 close 对齐")

    position = signal.shift(1).fillna(0).astype(int)
    daily_ret = close.pct_change().fillna(0.0)
    turnover = position.diff().abs()
    turnover.iloc[0] = float(abs(position.iloc[0]))
    cost = turnover * (fee + slippage)
    strategy_ret = position * daily_ret - cost

    equity = (1.0 + strategy_ret).cumprod()
    benchmark_ret = daily_ret.copy()
    benchmark_ret.iloc[0] = 0.0
    benchmark = (1.0 + benchmark_ret).cumprod()

    trades = _extract_trades(close, position)
    return BacktestResult(
        equity_curve=equity.rename("equity"),
        benchmark_curve=benchmark.rename("benchmark"),
        daily_returns=strategy_ret.rename("strategy_return"),
        positions=position.rename("position"),
        trades=trades,
        metrics=summarize(equity, strategy_ret),
        benchmark_metrics=summarize(benchmark, benchmark_ret),
    )


def _extract_trades(close: pd.Series, position: pd.Series) -> pd.DataFrame:
    rows: list[dict] = []
    previous = 0
    for date, pos in position.items():
        pos = int(pos)
        if pos == previous:
            continue
        side = "buy" if pos > previous else "sell"
        rows.append(
            {
                "date": date,
                "side": side,
                "price": float(close.loc[date]),
                "position_after": pos,
            }
        )
        previous = pos
    return pd.DataFrame(rows, columns=["date", "side", "price", "position_after"])

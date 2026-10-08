"""第 1 周冒烟：合成数据 -> RSI 信号 -> 回测指标。

真实 CSV 到位后，把 load_sample 换成 load_data。
"""

from __future__ import annotations

from src.backtest.engine import run_backtest
from src.data.loader import load_sample
from src.strategy.rsi import generate_signals
from src.viz.plots import metrics_table


def run_ticker(prices, ticker: str) -> None:
    close = prices.set_index("date")["close"]
    strategy = generate_signals(close)
    result = run_backtest(strategy["close"], strategy["signal"])
    table = metrics_table(result)
    print(f"\n=== {ticker} RSI 均值回归 ===")
    print(table.to_string(float_format=lambda value: f"{value:.4f}"))
    print(f"交易次数: {len(result.trades)}")
    if not result.trades.empty:
        print(result.trades.head().to_string(index=False))


def main() -> None:
    sample = load_sample("SAMPLE")
    run_ticker(sample, "SAMPLE")


if __name__ == "__main__":
    main()

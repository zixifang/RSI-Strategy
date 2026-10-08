"""数据加载接口。

角色 B 负责把 Kaggle 清洗结果放到 data/processed/{TICKER}.csv。
本文件提供：
- load_data：读取已清洗 CSV（B 的交付物）
- load_sample：合成价格，供角色 A 在真实数据到位前开发和测试
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

REQUIRED_COLUMNS = ["date", "open", "high", "low", "close", "volume"]


def load_data(
    tickers: list[str],
    start: str | None = None,
    end: str | None = None,
    data_dir: Path | None = None,
) -> pd.DataFrame:
    """读取一只或多只股票的日频 OHLCV。

    返回长表，列固定为 date, ticker, open, high, low, close, volume。
    date 为 datetime64[ns]，每个 ticker 内按 date 升序，索引为 RangeIndex。

    CSV 路径：{data_dir}/{TICKER}.csv，默认 data/processed/。
    CSV 必须包含 date, open, high, low, close, volume。
    """
    if not tickers:
        raise ValueError("tickers 不能为空")
    folder = Path(data_dir) if data_dir is not None else PROCESSED_DIR
    frames: list[pd.DataFrame] = []
    missing: list[str] = []
    for ticker in tickers:
        path = folder / f"{ticker.upper()}.csv"
        if not path.exists():
            missing.append(str(path))
            continue
        frame = _read_one(path, ticker.upper(), start, end)
        frames.append(frame)
    if missing:
        joined = "\n".join(missing)
        raise FileNotFoundError(
            "找不到清洗后的行情文件。请角色 B 将 CSV 放到 data/processed/。\n" + joined
        )
    return pd.concat(frames, ignore_index=True)


def load_sample(
    ticker: str = "SAMPLE",
    n_days: int = 400,
    seed: int = 7,
    start: str = "2022-01-03",
) -> pd.DataFrame:
    """生成带趋势和波动的合成收盘价，列格式与 load_data 相同。"""
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range(start=start, periods=n_days)
    shocks = rng.normal(0.0003, 0.012, size=n_days)
    close = 100.0 * np.exp(np.cumsum(shocks))
    open_ = np.r_[close[0], close[:-1]]
    high = np.maximum(open_, close) * (1 + rng.uniform(0.0, 0.008, size=n_days))
    low = np.minimum(open_, close) * (1 - rng.uniform(0.0, 0.008, size=n_days))
    volume = rng.integers(1_000_000, 5_000_000, size=n_days)
    return pd.DataFrame(
        {
            "date": dates,
            "ticker": ticker.upper(),
            "open": open_,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume,
        }
    )


def _read_one(path: Path, ticker: str, start: str | None, end: str | None) -> pd.DataFrame:
    frame = pd.read_csv(path)
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in frame.columns]
    if missing_cols:
        raise ValueError(f"{path.name} 缺少列: {missing_cols}")
    frame = frame.loc[:, REQUIRED_COLUMNS].copy()
    frame["date"] = pd.to_datetime(frame["date"])
    for col in ("open", "high", "low", "close", "volume"):
        frame[col] = pd.to_numeric(frame[col], errors="coerce")
    frame = frame.dropna(subset=["date", "close"])
    frame = frame.sort_values("date")
    if start is not None:
        frame = frame.loc[frame["date"] >= pd.Timestamp(start)]
    if end is not None:
        frame = frame.loc[frame["date"] <= pd.Timestamp(end)]
    frame["ticker"] = ticker
    return frame.loc[:, ["date", "ticker", "open", "high", "low", "close", "volume"]].reset_index(drop=True)

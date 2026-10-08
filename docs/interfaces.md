# 接口定义（第 1 周）

角色 A 维护这份约定。B / C / D 按这里的输入输出对接，不要各自发明列名。

策略：**RSI 均值回归（只做多）**。RSI(14) 跌破 30 开多，升破 70 平仓。期末目标是把「数据 → 策略 → 回测 → 图 → Docker」跑通，不追求收益。

## 1. 数据：`load_data`

实现位置：`src/data/loader.py`（角色 B）

```python
def load_data(
    tickers: list[str],
    start: str | None = None,
    end: str | None = None,
) -> pd.DataFrame
```

| 项 | 约定 |
|---|---|
| 文件 | `data/processed/{TICKER}.csv`，例如 `AAPL.csv` |
| 原始下载 | `data/raw/`，不提交到 Git |
| 返回列 | `date, ticker, open, high, low, close, volume` |
| `date` | `datetime64[ns]`，每个 ticker 内升序 |
| 索引 | 默认整数索引，不要用日期做索引 |
| 价格 | 未复权也可以，全组统一用同一份 close |
| 缺失 | 清洗后 `close` 不能为空；日期格式统一为 `YYYY-MM-DD` |

标的建议：AAPL、MSFT、GOOGL、AMZN、TSLA，先做这 5 只。

角色 A 在真实数据到来前用 `load_sample()` 生成同样列结构的合成行情。

## 2. 策略：`generate_signals`

实现位置：`src/strategy/rsi.py`（角色 A）

```python
def generate_signals(
    close: pd.Series,
    period: int = 14,
    oversold: float = 30.0,
    overbought: float = 70.0,
) -> pd.DataFrame
```

输入是**单只股票**的收盘价，索引为日期。一次只处理一只，多标的由调用方循环。

返回 DataFrame，索引与 `close` 相同：

| 列 | 类型 | 含义 |
|---|---|---|
| `close` | float | 收盘价 |
| `rsi` | float | Wilder RSI，前 `period` 根为 NaN |
| `signal` | int | `1` 持有多头，`0` 空仓 |

`signal` 在当日收盘后才能知道。回测不会用它赚当天的涨跌。

## 3. 回测：`run_backtest`

实现位置：`src/backtest/engine.py`（角色 A）

```python
def run_backtest(
    close: pd.Series,
    signal: pd.Series,
    fee: float = 0.001,
    slippage: float = 0.0,
) -> BacktestResult
```

执行规则：

- 仓位 = `signal.shift(1)`，避免未来函数
- 只做多，满仓或空仓
- 换仓成本 = `|仓位变化| * (fee + slippage)`
- 基准是同一段收盘价的买入持有

`BacktestResult` 字段：

| 字段 | 类型 | 给谁用 |
|---|---|---|
| `equity_curve` | Series，起点约 1.0 | 角色 C 画策略净值 |
| `benchmark_curve` | Series，起点约 1.0 | 角色 C 画买入持有 |
| `daily_returns` | Series | 复现夏普 |
| `positions` | Series，0/1 | 实际持仓（已后移一天） |
| `trades` | DataFrame | 列：`date, side, price, position_after`；`side` 为 `buy` 或 `sell` |
| `metrics` | dict | `cumulative_return`, `max_drawdown`, `sharpe` |
| `benchmark_metrics` | dict | 同上，基准 |

指标口径：

- `cumulative_return`：净值终值 / 净值起点 − 1
- `max_drawdown`：小于等于 0，例如 `-0.18` 表示最大回撤 18%
- `sharpe`：日收益均值 / 日收益标准差 × √252，无风险利率按 0

## 4. 可视化

实现位置：`src/viz/plots.py`（角色 C）

```python
def plot_price_signals(strategy: pd.DataFrame, ticker: str, save_path: Path | None = None) -> None
def plot_equity(result: BacktestResult, ticker: str, save_path: Path | None = None) -> None
def plot_drawdown(result: BacktestResult, ticker: str, save_path: Path | None = None) -> None
def metrics_table(result: BacktestResult) -> pd.DataFrame
```

`metrics_table` 已可用，返回两行：`strategy` 与 `buy_and_hold`。三张图第 1 周先留接口，角色 C 第 2 周起实现。图片请写到 `output/`。

## 5. 怎么串起来

```python
from src.data.loader import load_data
from src.strategy.rsi import generate_signals
from src.backtest.engine import run_backtest

prices = load_data(["AAPL"], start="2018-01-01", end="2023-12-31")
aapl = prices.loc[prices["ticker"] == "AAPL"].set_index("date")
strategy = generate_signals(aapl["close"])
result = run_backtest(strategy["close"], strategy["signal"])
```

本地还没有 CSV 时，把 `load_data` 换成 `load_sample("AAPL")`。入口脚本是 `python -m src.main`。

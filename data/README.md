# 数据目录

| 路径 | 内容 | 是否提交 |
|---|---|---|
| `data/raw/` | Kaggle 原始文件 | 否 |
| `data/processed/{TICKER}.csv` | 清洗后的日频行情 | 文件不大时可以提交；太大则只在 Docker 卷里挂载 |

`processed` 下每个 CSV 的列：`date, open, high, low, close, volume`。读取方式见 `docs/interfaces.md`。

建议标的：AAPL、MSFT、GOOGL、AMZN、TSLA。来源请在角色 B 的数据说明里写上 Kaggle 数据集名称和链接。

# 美股 RSI 均值回归回测

期末数据科学小组项目的最小可行版本：用日频 OHLCV 跑通 **RSI 均值回归 → 回测指标 → 图表 → Docker 复现**。策略是否赚钱不是验收标准，链路能复现才是。

当前策略：RSI(14) 低于 30 开多，高于 70 平仓。只做多，信号次日生效。

## 分工

| 角色 | 模块 | 第 1 周交付 |
|---|---|---|
| A | `src/strategy`、`src/backtest`、接口文档 | 已建立仓库与接口，冒烟脚本可跑 |
| B | `src/data/loader.py`、`data/processed` | Kaggle 数据与清洗 |
| C | `src/viz/plots.py`、`output/` | 确认三张图的清单 |
| D | `Dockerfile`、`docker-compose.yml` | 镜像里能看到 Python 版本 |
| E | 汇报材料、审查记录 | PPT 框架与 README 口径（仓库已由 A 建好） |

接口以 [docs/interfaces.md](docs/interfaces.md) 为准。分支规则见 [docs/branching.md](docs/branching.md)。

## 本地运行

需要 Python 3.10 及以上。本机开发环境是 3.12，Docker 目标版本是 3.10。

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest
python -m src.main
```

`src.main` 使用合成行情。角色 B 把 CSV 放到 `data/processed/` 之后，按接口文档把入口改成 `load_data`。

也可以运行 `.\run.ps1`，它会创建虚拟环境、安装依赖、跑测试并打印指标。

## Docker

角色 D 负责把下面两条命令收成稳定的一键流程。骨架已经放在仓库里：

```powershell
docker compose build
docker compose run --rm backtest
```

数据通过卷挂载 `./data` 和 `./output`，不用把大文件打进镜像。

## 服务器

`方向.txt` 里提到的 Slurm 只作为以后上机算力的可选入口，见 `slurm/run.sbatch`。第 1 周不依赖集群。

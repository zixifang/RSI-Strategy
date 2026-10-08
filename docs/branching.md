# 分支策略

仓库由角色 A 建立。角色 E 继续维护 README 口径、PR 审查记录和汇报材料。

## 长期分支

| 分支 | 用途 |
|---|---|
| `main` | 可演示的稳定版本。只接受来自 `develop` 的 PR |
| `develop` | 日常集成。功能分支都合并到这里 |

## 功能分支

命名：`feature/<角色>-<内容>`

| 例子 | 谁 |
|---|---|
| `feature/a-rsi` | 角色 A，策略或回测 |
| `feature/b-loader` | 角色 B，数据清洗与 `load_data` |
| `feature/c-plots` | 角色 C，图表 |
| `feature/d-docker` | 角色 D，镜像与一键运行 |
| `feature/e-readme` | 角色 E，文档与汇报材料 |

从 `develop` 拉出，改完开 PR 回 `develop`。不要直接往 `main` 推代码。

## 提交说明

用一句中文或英文说清原因，例如：

- `实现 RSI 开平仓，并后移一天计算收益`
- `对齐 load_data 的列名与日期类型`

## 合并前

- 至少 1 人审查（建议角色 A 看接口是否被改坏）
- `pytest` 通过
- 改了数据列、函数参数或返回字段时，同步改 `docs/interfaces.md`

# 第097讲配套产物｜双均线策略

本目录提供可由 WorkBuddy 或 TRAE 生成并验证的完整 Python/R 参考产物。两种语言使用相同输入、参数、信号时点、交易成本和绩效公式。

## 文件

- [Python 完整实现](<python/dual_moving_average.py>)
- [R 完整实现](<r/dual_moving_average.R>)
- [合成演示行情](<input/price.csv>)
- [Python 逐日运行结果](<output/python_daily.csv>)
- [R 逐日运行结果](<output/r_daily.csv>)
- [Python 绩效指标](<output/python_metrics.csv>)
- [R 绩效指标](<output/r_metrics.csv>)
- [Python/R 跨语言对账报告](<validation/parity_report.md>)
- [WorkBuddy 与 TRAE 操作方案](<../../WorkBuddy与TRAE操作方案.md>)
- [第097讲正文](<../../模块10-知行·实战演练/第097讲-动手写一个双均线策略（Python与R代码实操）.md>)

## 输入

目录中已附带一份合成演示数据 `input/price.csv`，用于验证运行流程，不代表真实市场。替换成自己的研究数据时，至少包含：

| 字段 | 类型 | 说明 |
|---|---|---|
| `date` | 日期 | 可被 Python 与 R 解析的交易日期 |
| `close` | 正数 | 已选定统一复权口径的收盘价 |

脚本会按日期升序排列，并对重复日期保留第一条。数据不得少于长均线窗口，默认至少 60 行。

## 默认参数

| 参数 | 默认值 | 含义 |
|---|---:|---|
| `short` | 20 | 短均线窗口 |
| `long` | 60 | 长均线窗口 |
| `fee` | 0.0005 | 每单位换手率对应的交易成本 |
| `periods` | 252 | 日频年化周期 |

## 运行

在本目录打开终端。

- Python：运行 `python3 python/dual_moving_average.py`。
- R：运行 `Rscript r/dual_moving_average.R`。

两个脚本也支持 `--input`、`--daily-output`、`--metrics-output`、`--short`、`--long`、`--fee` 和 `--periods` 参数。修改参数时必须同时修改两端。

## 输出

默认生成：

- `output/python_daily.csv` 与 `output/r_daily.csv`
- `output/python_metrics.csv` 与 `output/r_metrics.csv`
- `validation/parity_report.md` 记录两端对账结论；替换输入或参数后应重新生成该报告。

逐日结果应核对 `date`、`signal`、`position`、`turnover`、`strategy_ret` 和 `equity`。除浮点舍入外，两端结果应一致；建议绝对容差使用 `1e-10`。

## 环境

- Python 3 与 `pandas`
- R 4.x；R 版本只使用基础包和 `stats`

## 风险限制

代码仅用于研究教学，不包含真实撮合、复权处理、公司行动、市场冲击模型、停牌与涨跌停、部分成交、现金利息、账户接口或生产级风控，不得直接连接真实账户。

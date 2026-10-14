# 第097讲 动手写一个双均线策略（Python与R代码实操）

> 所属模块：模块10｜知行·实战演练  
> 建议时长：15–20 分钟  
> 内容状态：已完成（课程版 v1.0）

> 风险提示：本文仅用于量化投资知识教育，不构成任何投资建议。实盘交易部署会产生真实损失，必须经过授权、测试和独立风控。

## 本讲目标

- 分别使用 Python 与 R 实现无前视偏差的双均线基线。
- 使用 WorkBuddy 或 TRAE 生成、运行并验收两种语言的完整课程产物。
- 确保两种语言使用相同输入、参数、信号时点、交易成本和绩效口径。
- 生成目标仓位、策略收益率、交易成本、净值和基础绩效指标。
- 理解代码每一步的金融含义，并能够逐行对账。

## 规则

使用收盘价计算 20/60 日均线；短均线高于长均线时持有，反之空仓。收盘后得到信号，下一交易日生效。

## 先获取本讲课程产物

本讲的 Python 与 R 代码被定义为 WorkBuddy 或 TRAE 的可验收产物。读者可以直接查看参考产物，也可以按照统一提示词让任一工具重新生成并验证：

- [配套产物说明](<../配套产物/第097讲-双均线策略/README.md>)
- [Python 完整产物](<../配套产物/第097讲-双均线策略/python/dual_moving_average.py>)
- [R 完整产物](<../配套产物/第097讲-双均线策略/r/dual_moving_average.R>)
- [Python/R 跨语言对账报告](<../配套产物/第097讲-双均线策略/validation/parity_report.md>)
- [WorkBuddy 与 TRAE 通用操作方案](<../WorkBuddy与TRAE操作方案.md>)

参考产物可直接从终端接收输入和输出路径、均线窗口、交易成本与年化周期参数。下方代码用于解释核心计算，完整输入校验、参数解析和文件输出以配套产物为准。

## 用 WorkBuddy 完成本讲

1. 新建 **Coding Mode** 任务，选择一个仅用于本讲的工作文件夹，并保持 **Default Permissions**。
2. 加入本讲正文、术语规范和 `input/price.csv`。
3. 要求 WorkBuddy 同时生成 Python/R 源文件、分别运行两端、输出逐日与指标 CSV，并生成跨语言对账报告。
4. 在结果面板检查 Artifacts、All Files、Changes 和 Preview；若有差异，让它定位第一个不一致的日期与字段。

针对本讲可发送：

> 按第097讲规则实现 20/60 日双均线策略，交易成本为每单位换手率 0.0005，日频年化周期为 252。收盘后生成信号，仓位必须滞后一日。请同时生成完整 Python 与 R 产物，分别输出逐日结果和绩效指标，并以绝对容差 `1e-10` 逐列核对信号、仓位、换手率、策略收益率和净值。不要连接真实账户。

## 用 TRAE 完成本讲

1. 在 TRAE Work 中选择 **Code Mode**，或在 TRAE IDE 中打开本讲工作文件夹；确认运行环境可调用 Python 3 和 `Rscript`。
2. 把本讲正文、术语规范和输入数据加入工作区，在 Agent 中发送与 WorkBuddy 相同的任务指令。
3. 审阅文件变更与终端命令后，让 Agent 分别运行 Python 和 R 脚本。
4. 检查变更视图、终端输出、README 预览和对账报告；任何超出容差的差异都必须修复后重跑。

## Python 产物核心实现

假设 `price.csv` 至少包含 `date,close`：

```python
import pandas as pd

SHORT, LONG = 20, 60
FEE = 0.0005

df = pd.read_csv("price.csv", parse_dates=["date"])
df = df.sort_values("date").drop_duplicates("date").set_index("date")

df["ret"] = df["close"].pct_change()
df["ma_short"] = df["close"].rolling(SHORT, min_periods=SHORT).mean()
df["ma_long"] = df["close"].rolling(LONG, min_periods=LONG).mean()

# t 日收盘后才知道 signal，因此 t+1 日仓位使用 shift(1)
df["signal"] = (df["ma_short"] > df["ma_long"]).astype(float)
df["position"] = df["signal"].shift(1).fillna(0.0)

df["turnover"] = df["position"].diff().abs().fillna(0.0)
df["strategy_ret"] = (
    df["position"] * df["ret"] - FEE * df["turnover"]
).fillna(0.0)
df["equity"] = (1.0 + df["strategy_ret"]).cumprod()
```

## 基本绩效

```python
PERIODS = 252
n = len(df)
ann_return = df["equity"].iloc[-1] ** (PERIODS / n) - 1
ann_vol = df["strategy_ret"].std(ddof=1) * PERIODS ** 0.5
sharpe = (
    df["strategy_ret"].mean() * PERIODS / ann_vol
    if ann_vol > 0
    else float("nan")
)
peak = df["equity"].cummax()
max_drawdown = (df["equity"] / peak - 1.0).min()
print(ann_return, ann_vol, sharpe, max_drawdown)
```

## R 产物核心实现

R 版本只使用基础包，并与 Python 版本保持相同变量和计算口径。

### 策略与净值

```r
SHORT <- 20L
LONG <- 60L
FEE <- 0.0005

df <- read.csv("price.csv", stringsAsFactors = FALSE)
df$date <- as.Date(df$date)
df <- df[order(df$date), ]
df <- df[!duplicated(df$date), ]
row.names(df) <- NULL

roll_mean <- function(x, n) {
  as.numeric(stats::filter(x, rep(1 / n, n), sides = 1))
}

df$ret <- c(NA_real_, diff(df$close) / head(df$close, -1L))
df$ma_short <- roll_mean(df$close, SHORT)
df$ma_long <- roll_mean(df$close, LONG)

# t 日收盘后才知道 signal，因此 t+1 日的仓位滞后一日
df$signal <- as.numeric(df$ma_short > df$ma_long)
df$signal[is.na(df$signal)] <- 0
df$position <- c(0, head(df$signal, -1L))

df$turnover <- c(0, abs(diff(df$position)))
df$strategy_ret <- df$position * df$ret - FEE * df$turnover
df$strategy_ret[is.na(df$strategy_ret)] <- 0
df$equity <- cumprod(1 + df$strategy_ret)
```

### 基础绩效

```r
PERIODS <- 252
n <- nrow(df)
ann_return <- tail(df$equity, 1)^(PERIODS / n) - 1
ann_vol <- stats::sd(df$strategy_ret) * sqrt(PERIODS)
sharpe <- if (is.finite(ann_vol) && ann_vol > 0) {
  mean(df$strategy_ret) * PERIODS / ann_vol
} else {
  NA_real_
}
peak <- cummax(df$equity)
max_drawdown <- min(df$equity / peak - 1)
print(c(ann_return, ann_vol, sharpe, max_drawdown))
```

## Python 与 R 结果对账

两个版本使用相同 `price.csv` 时，应逐日比较 `ma_short`、`ma_long`、`signal`、`position`、`turnover`、`strategy_ret` 和 `equity`。移动平均线形成前的缺失值和浮点误差可能造成极小差异；若仓位或净值出现方向性差异，应先逐行定位。

## 这些教学产物还缺什么

真实项目还要处理复权、分红、交易日历、滑点、市场冲击成本、无法成交、现金利息和信号执行价格。这里是研究基线，不是可直接连接账户的实盘交易程序。

## 自检

确认完整 Python/R 源文件和 README 均已生成；仓位已滞后一日；长均线形成前仓位为零；交易成本只在仓位变化时扣；两端使用相同数据和参数；逐日结果已在 `1e-10` 容差内对账；最后再用小样本逐行手算验证。

<!-- 课程版-v1.0-完稿补充 -->

## 实战交付：让别人能够独立复现

围绕“动手写一个双均线策略（Python与R代码实操）”形成可交付的研究闭环。完工标准不是代码在作者电脑上运行过一次，而是另一位读者能按说明重建环境、运行测试并解释输出。

1. 冻结需求、输入字段、参数、信号时点、成本口径和输出结构。
2. 把数据校验、策略逻辑、账本、指标、日志和异常处理拆成可测试模块。
3. 使用同一份输入分别运行 Python 与 R，实现逐日结果与指标对账。
4. 保留 README、运行命令、测试记录、已知限制和上线前检查清单。

## 常见误区与修正

- 只交付代码片段而没有输入、环境和运行说明；这不构成可复现产物。
- Python 与 R 使用不同默认参数或缺失值规则；跨语言对账必须逐列进行。
- 把回测通过等同于可实盘；模拟交易、权限隔离、监控和故障恢复仍需独立验收。

## 实战验收清单

- [ ] 从干净环境可按 README 一次运行成功
- [ ] 输入校验和关键逻辑有自动测试
- [ ] Python 与 R 输出在约定容差内一致
- [ ] 日志、监控、异常恢复和风险限制均有文档

## 本讲小结

- 双均线的关键不是均线函数，而是信号、目标仓位和执行时点的严格分离。
- Python 与 R 实现必须使用同一数据、参数和交易成本口径。
- 夏普比率使用平均单期收益率年化，年化收益率使用净值几何复合，两者不能混算。
- WorkBuddy 与 TRAE 都必须交付可运行文件、结果数据和跨语言对账结论。
- 最小代码应先逐行对账，再扩展真实撮合。

## 课后练习

任选 WorkBuddy 或 TRAE，分别在 Python 与 R 完整产物中加入 `3×ATR` 吊灯止损，确保两种实现的信号时点和跳空处理一致，并提交两端逐日结果与跨语言对账报告。

## 下期预告

下一讲：**第098讲 在聚宽/米筐上完成一次完整回测并看懂报告**。

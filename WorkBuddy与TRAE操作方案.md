# 量化投资100讲｜WorkBuddy 与 TRAE 操作方案

> 适用范围：课程中所有包含可执行代码的讲次。  
> 交付原则：Python 与 R 代码是 WorkBuddy 或 TRAE 生成、运行和验证后的课程产物，不只是正文中的示意片段。

## 一、读者最终应拿到什么

每个代码讲次采用同一套产物契约：

| 产物 | 用途 |
|---|---|
| `python/<策略名>.py` | 可独立运行的 Python 完整实现 |
| `r/<策略名>.R` | 与 Python 口径等价的 R 完整实现 |
| `output/python_daily.csv` | Python 逐日信号、仓位、收益率与净值 |
| `output/r_daily.csv` | R 逐日信号、仓位、收益率与净值 |
| `output/python_metrics.csv` | Python 绩效指标 |
| `output/r_metrics.csv` | R 绩效指标 |
| `validation/parity_report.md` | Python 与 R 的逐列差异、容差和结论 |
| `README.md` | 输入字段、依赖、运行方法、输出解释与风险限制 |

正文可以展示核心代码，但读者应优先下载或让工具生成完整产物。除语言语法外，两种实现必须使用相同的数据、参数、信号时点、交易成本和指标公式。

## 二、开始前准备

1. 为每一讲创建独立工作文件夹，不直接在唯一一份重要数据上操作。
2. 把课程讲义、[课程术语与代码规范](<课程术语与代码规范.md>)和输入数据放入或授权给该工作区。
3. 行情输入统一为 `input/price.csv`；具体讲次可以扩展字段，但必须在 README 中说明。
4. 本机准备 Python 3、所需 Python 包和 R；确认终端能够调用 `python3` 与 `Rscript`。
5. 默认保留工具的安全确认，不向任务提供账户密钥、券商凭证或生产环境写权限。

## 三、WorkBuddy 操作方案

WorkBuddy 适合希望通过自然语言直接获得文件产物的读者。

1. 新建任务并选择 **Coding Mode**。
2. 点击 **Select Folder**，选择本讲的独立工作文件夹。
3. 保持 **Default Permissions**；只有在隔离、可恢复的测试目录中才考虑临时扩大权限。
4. 用 `@` 引用讲义、术语规范和 `input/price.csv`，或把这些文件拖入任务。
5. 发送下方“统一任务指令”，要求先列出文件计划，再生成文件并运行验证。
6. 若 WorkBuddy 请求执行命令，检查命令、路径和影响范围后再确认。
7. 在右侧结果面板依次检查 **Artifacts、All Files、Changes、Preview**，确认 Python/R 文件、CSV 结果与对账报告齐全。
8. 若两种语言结果不一致，继续要求它逐日比较第一个差异行，不接受只凭最终指标“看起来接近”的结论。

## 四、TRAE 操作方案

TRAE 提供面向非工程任务的 TRAE Work 和面向开发者的 TRAE IDE。两者都能用于本课程；需要查看代码差异和逐步调试时，优先使用 TRAE IDE。TRAE 可协助配置 Python 环境，R 代码仍需本机安装 R，并通过终端调用 `Rscript`。

### TRAE Work

1. 新建任务并选择 **Code Mode**，把本讲工作文件夹设为任务目录。
2. 加入讲义、术语规范和输入数据，发送下方“统一任务指令”。
3. 检查生成的文件、运行进度和结果预览，要求它分别运行 Python 与 R 版本。
4. 若需要逐行审阅代码或调试运行环境，可继续在 TRAE IDE 中打开同一文件夹。

### TRAE IDE

1. 用 TRAE IDE 打开本讲的独立工作文件夹。
2. 将讲义、术语规范和输入数据加入工作区；需要额外文档时可通过 `#Doc` 提供 Markdown 上下文。
3. 打开 Agent，发送下方“统一任务指令”，明确要求同时生成 Python 与 R 产物；部分旧版本可能仍显示 Builder。
4. 审阅 Agent 的计划、文件变更和终端命令，再允许写入与运行。
5. 让 Agent 分别执行 Python 和 R 脚本，并保留终端错误信息；缺少依赖时只安装任务所需的最小依赖。
6. 在变更视图检查完整代码差异，在 Markdown 预览中检查 README 和对账报告。
7. 要求 Agent 输出第一个不一致的日期、字段、两端数值和绝对误差，修复后重新运行全部验收项。

## 五、统一任务指令

把下列内容中的方括号替换为本讲信息，然后交给 WorkBuddy 或 TRAE：

> 阅读 `[本讲讲义]`、`课程术语与代码规范.md` 和 `input/price.csv`。请先列出产物计划，再实现 `[策略名称]`。同时生成完整、可独立运行的 Python 与 R 版本，并使用相同输入字段、参数、信号时点、交易成本、缺失值处理和绩效公式。分别输出逐日结果与指标 CSV，再生成 `validation/parity_report.md`。逐列核对日期、信号、目标仓位、换手率、策略收益率和净值；除浮点误差外必须一致，默认绝对容差为 `1e-10`。若环境缺少依赖，先说明最小安装项；不要连接真实账户，不要读取工作区之外的数据，不要把密钥写入文件。完成后列出所有产物、运行命令、测试结果和仍未覆盖的实盘交易风险。

## 六、统一验收清单

- Python 与 R 源文件均存在，且不是伪代码。
- 两个脚本可以从干净终端独立运行，并返回成功状态。
- 输入校验、排序、去重、缺失值处理和异常提示一致。
- 收盘后生成的信号滞后一周期形成仓位，不存在前视偏差。
- 参数、交易成本、年化周期和无风险收益率口径一致。
- 两份逐日结果的行数、日期、字段和仓位完全一致。
- 浮点字段差异在约定容差内；超过容差时报告第一个差异点。
- README 能让未参与生成过程的读者复现结果。
- 产物明确标注研究教学用途，不连接真实账户。

## 七、当前示例产物

- [第097讲双均线策略产物说明](<配套产物/第097讲-双均线策略/README.md>)
- [Python 完整实现](<配套产物/第097讲-双均线策略/python/dual_moving_average.py>)
- [R 完整实现](<配套产物/第097讲-双均线策略/r/dual_moving_average.R>)

## 官方参考

- [WorkBuddy 快速开始](https://www.workbuddy.ai/docs/workbuddy/Quickstart)
- [WorkBuddy 创建任务与结果面板](https://www.workbuddy.ai/docs/workbuddy/Create-Task)
- [WorkBuddy 权限模式](https://www.workbuddy.ai/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Permission-Modes)
- [TRAE IDE](https://www.trae.ai/ide/)
- [TRAE Work 产品说明](https://www.trae.ai/blog/trae_work_0609)
- [TRAE 更新记录](https://www.trae.ai/changelog)

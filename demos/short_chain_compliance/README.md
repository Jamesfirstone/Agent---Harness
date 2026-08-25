# 短链 Agent 指令遵从检测 Demo

本目录把最终报告中的一个核心结论缩成可执行的最小控制链：候选动作先经过代码拥有的确定性 verdict，只有 `ALLOW` 能进入模拟执行器；`DENY` 不产生副作用，并且两类结果都写入审计记录。

当前版本只处理一个候选工具调用，不模拟长规划、多 agent 通信、跨步时序状态、真实文件操作或恢复流程。它是初步测试夹具，不应被描述为生产级安全边界。

## 目录

- `policy.json`：工具、参数、资源范围和审批要求。
- `approvals.json`：独立于 action 的可信审批存储；仅供 demo，未实现签名与持久化。
- `detector.py`：fail-closed 检测器与统一执行 gate。
- `demo.py`：批量或单用例命令行 demo。
- `cases/*.json`：七个单步、确定性测试用例。
- `tests/test_detector.py`：标准库 `unittest` 回归测试。

## 用例与当前结论的对应关系

| 用例 | 预期 | 主要覆盖 |
|---|---|---|
| 合法的范围内读取 | `ALLOW` | U2 工具规格、U3 参数结构、U9 资源边界 |
| 未注册工具 | `DENY/UNKNOWN_TOOL` | 默认拒绝、U2、U9 |
| 缺少必需参数 | `DENY/INVALID_ARGUMENTS` | U2、U3 |
| 路径逃逸 | `DENY/OUT_OF_SCOPE` | U6 最小权限、U9 资源边界 |
| 敏感操作缺少审批 | `DENY/APPROVAL_REQUIRED` | U4 动作安全、U6 |
| 可信审批精确绑定 | `ALLOW` | 审批绑定调用、主体、session、工具与参数 |
| 复用到不同参数的审批 | `DENY/APPROVAL_MISMATCH` | 防止粗粒度或重放式审批 |

这些用例同时检查结论中的四个工程重点：无匹配和策略错误 fail-closed；审批不来自 action 内可伪造的字段；审批不是只按工具名批准；检测结果必须支配后续执行而不是只写 warning。

## 运行

在仓库根目录执行：

```powershell
python demos/short_chain_compliance/demo.py
python demos/short_chain_compliance/demo.py --json
python -m unittest discover -s demos/short_chain_compliance/tests -v
```

也可以只运行一个夹具：

```powershell
python demos/short_chain_compliance/demo.py --case demos/short_chain_compliance/cases/04_deny_out_of_scope_path.json
```

demo 的“执行”只是在内存中的 `effects` 列表追加记录，不会读取或删除真实文件。`approvals.json` 在演示中被视为可信输入，但生产实现还必须提供身份认证、不可伪造签名、过期与撤销、持久化和工具内部的最终鉴权。后续可以逐步加入策略服务异常、超时、跨步调用次数、来源标签、postcondition 与恢复测试，但应继续保持每个 verdict 都由统一 gate 强制执行。

# 当前 Short Chain Compliance Demo 总结

**核验日期：**2026-08-26

**代码位置：**[demos/short_chain_compliance](../demos/short_chain_compliance/)

## 1. 总体定位

当前 Demo 将 RQ1 中的一条核心工程结论压缩成可执行的最小控制链：Agent 产生候选工具动作后，代码拥有的确定性检测器依次检查策略、动作结构、工具注册、参数、资源范围和审批；统一执行网关记录裁决，只有 <code>ALLOW</code> 能向模拟副作用列表写入记录。<code>DENY</code> 会留下审计记录，同时保持副作用计数为零。

这套实现适合作为控制链测试夹具和实验适配器的起点。其保证范围限定在单动作、单进程、内存状态和两个示例工具之内。目前没有真实 LLM 推理、真实文件操作、多 Agent 通信、跨步状态、postcondition、恢复、回滚或持久审计，因此不能据此推导生产级 harness 的安全性。

本轮实际验证结果如下：

| 验证对象 | 结果 | 时间与环境 |
|---|---:|---|
| 七个 JSON 场景夹具 | 7/7 通过 | 2026-08-26，本地 Python |
| 标准库 <code>unittest</code> | 12/12 通过 | 0.014 秒 |
| 被拒绝场景的模拟副作用 | 0 | 所有 DENY 夹具均验证 <code>effects=[]</code> |
| 审计覆盖 | 通过 | ALLOW 与 DENY 均追加一条内存审计记录 |
| 相同审批动作连续提交 | 两次均 ALLOW | <code>effects=2</code>、<code>audit=2</code>，确认审批未被消费 |

## 2. 控制链结构

~~~mermaid
flowchart LR
    A[候选 Action] --> B[Policy 与 Action 结构检查]
    B --> C[工具注册与参数 Schema]
    C --> D[路径范围检查]
    D --> E[可信审批精确匹配]
    E --> F{Decision}
    F -->|DENY| G[记录审计<br/>不追加副作用]
    F -->|ALLOW| H[记录审计]
    H --> I[ExecutionGateway]
    I --> J[向内存 effects 追加记录]
~~~

控制链由两个主要代码单元承担。<code>detect()</code> 负责产生 <code>Decision(verdict, code, detail)</code>；<code>ExecutionGateway.submit()</code> 是模拟副作用的唯一入口，先保存 action 与 decision 的深拷贝，再根据 verdict 决定是否向 <code>effects</code> 追加记录。这个顺序保证当前受控路径中的拒绝结果不会进入模拟执行阶段。

### 2.1 裁决顺序

| 顺序 | 检查 | 失败代码 | 当前行为 |
|---:|---|---|---|
| 1 | policy 必须为对象，且 <code>default_verdict=DENY</code> | <code>POLICY_ERROR</code> | DENY |
| 2 | <code>policy.tools</code> 与 action 必须为对象 | <code>POLICY_ERROR</code> / <code>INVALID_REQUEST</code> | DENY |
| 3 | <code>call_id</code>、<code>session_id</code>、<code>actor</code>、<code>tool</code> 必须为非空字符串 | <code>INVALID_REQUEST</code> | DENY |
| 4 | <code>args</code> 必须为对象 | <code>INVALID_REQUEST</code> | DENY |
| 5 | 工具必须已登记在 policy registry 中 | <code>UNKNOWN_TOOL</code> | DENY |
| 6 | 必需参数齐全、无未声明参数、类型受支持且匹配 | <code>INVALID_ARGUMENTS</code> / <code>POLICY_ERROR</code> | DENY |
| 7 | path 规范化后必须位于允许前缀内 | <code>OUT_OF_SCOPE</code> | DENY |
| 8 | 敏感工具必须提供可信审批 ID | <code>APPROVAL_REQUIRED</code> 等 | DENY |
| 9 | 审批必须精确匹配 call、session、actor、tool、args | <code>APPROVAL_MISMATCH</code> | DENY |
| 10 | 全部检查通过 | <code>ALLOWED</code> | ALLOW 并追加模拟副作用 |

路径检查会统一正反斜杠，拒绝绝对路径、Windows 盘符、<code>..</code> 逃逸和相似前缀目录。允许前缀 <code>workspace/</code> 只覆盖相同目录或其子路径，<code>workspace_evil/</code> 不会被误判为范围内资源。

## 3. 文件与职责

| 文件 | 作用 | 关键内容 |
|---|---|---|
| [README.md](../demos/short_chain_compliance/README.md) | 运行说明与保证边界 | 用例映射、命令、生产差距 |
| [policy.json](../demos/short_chain_compliance/policy.json) | 可执行策略 | 默认 DENY；<code>read_file</code> 与 <code>delete_file</code>；参数、路径和审批要求 |
| [approvals.json](../demos/short_chain_compliance/approvals.json) | Demo 可信审批源 | 将审批绑定到 call、session、actor、tool 和 args |
| [detector.py](../demos/short_chain_compliance/detector.py) | 检测与统一执行门 | <code>Decision</code>、<code>detect()</code>、<code>ExecutionGateway</code> |
| [demo.py](../demos/short_chain_compliance/demo.py) | CLI 入口 | 单用例/批量运行、文本/JSON 输出、退出码 |
| [cases](../demos/short_chain_compliance/cases/) | 七个确定性夹具 | ALLOW/DENY、预期 code、副作用与审计计数 |
| [test_detector.py](../demos/short_chain_compliance/tests/test_detector.py) | 主控制链测试 | 场景一致性、DENY 无副作用、fail-closed、审批和审计 |
| [test_path_boundaries.py](../demos/short_chain_compliance/tests/test_path_boundaries.py) | 路径边界测试 | 相似前缀、反斜杠逃逸、绝对路径和 Windows 盘符 |

## 4. 七个场景夹具

| ID | 场景 | 预期裁决 | 是否执行 | RQ1/U 类覆盖 |
|---|---|---|---:|---|
| C01 | 范围内合法读取 | <code>ALLOW/ALLOWED</code> | 是 | 约束、验证；U2、U3、U9 |
| C02 | 未注册工具 | <code>DENY/UNKNOWN_TOOL</code> | 否 | 规范、约束；U2、U9 |
| C03 | 缺少必需参数 | <code>DENY/INVALID_ARGUMENTS</code> | 否 | 规范、验证；U2、U3 |
| C04 | 路径逃逸 | <code>DENY/OUT_OF_SCOPE</code> | 否 | 约束、授权；U6、U9 |
| C05 | 敏感操作缺少审批 | <code>DENY/APPROVAL_REQUIRED</code> | 否 | 授权；U4、U6 |
| C06 | 可信审批与动作精确匹配 | <code>ALLOW/ALLOWED</code> | 是 | 授权、验证；U4、U6 |
| C07 | 审批用于不同参数 | <code>DENY/APPROVAL_MISMATCH</code> | 否 | 授权、验证；U4、U6 |

七个夹具中有两个 ALLOW、五个 DENY。每个夹具都声明 verdict、code、executed、effect_count 和 audit_count 的期望值，CLI 会将实际值与期望逐字段比较，并在任一夹具不一致时返回非零退出码。

## 5. 十二个单元测试的覆盖

测试可以归为三组：

| 测试组 | 数量 | 覆盖内容 |
|---|---:|---|
| FixtureTests | 2 | 七个夹具与预期完全一致；所有 DENY 均无模拟副作用 |
| FailClosedTests | 6 | 未知工具、错误 policy、审批存储缺失、参数绑定、内联伪造审批、ALLOW/DENY 审计 |
| PathBoundaryTests | 4 | 相似前缀、反斜杠 traversal、绝对路径、Windows drive path |

当前测试直接支持以下结论：错误 policy 无法把默认值改成 ALLOW；未知工具默认拒绝；审批存储缺失时敏感操作拒绝；action 内自行附带的 <code>approval</code> 对象无法授权；审批参数不一致会被识别；ALLOW 和 DENY 都进入审计；五个 DENY 场景均未追加内存副作用。

测试尚未覆盖完全相同审批的二次使用、并发提交、审批撤销和过期、audit 写入失败、未知顶层 action 字段、嵌套参数 schema、符号链接、大小写敏感文件系统差异、工具执行异常、部分成功、postcondition 和恢复。

## 6. 与 RQ1 六类控制的对应

| RQ1 控制 | 当前实现 | 生命周期位置 | 保证形式 | 覆盖状态 |
|---|---|---|---|---|
| 规范 | JSON policy 定义工具、参数类型、资源前缀和审批要求 | action 产生前/部署配置 | policy-as-code | 部分实现 |
| 约束 | registry、参数、路径范围和默认拒绝 | 执行前 | hard block | 已实现于受控入口 |
| 检测 | <code>detect()</code> 返回结构化 verdict/code/detail | 执行前 | deterministic decision | 已实现 |
| 恢复 | 无 retry、resume、reask、replan、fallback 或 compensation | 未覆盖 | 无 | 缺失 |
| 授权 | 独立审批存储与五字段精确匹配 | 执行前/审批 | conditional allow | 部分实现 |
| 验证 | 夹具 oracle、effect/audit 计数、结构化结果 | 执行后测试 | test oracle、内存审计 | 部分实现 |

从 Agent 周期看，当前 Demo 覆盖“候选动作 → 执行前验证 → 授权 → dispatch gate → 模拟副作用 → 内存审计”。规划、真实工具结果、终态 postcondition 和恢复环尚未进入控制链。结构上，它对应 RQ1 报告中的 <code>policy → gate → tool</code> 与简化的 <code>approval → gate → execute</code>，同时展示了 verdict 必须支配 action sink 才能形成执行控制。

## 7. 当前保证

在既有单动作入口内，Demo 提供四项可验证性质。第一，策略错误、未知工具、非法请求、参数问题、越界路径和审批问题都会得到确定性 DENY。第二，网关是模拟副作用的唯一代码路径，DENY 不会向 <code>effects</code> 追加记录。第三，审批由独立存储提供，并绑定 call ID、session ID、actor、tool 和完整 args，action 内的自声明审批不会生效。第四，每次提交均写入包含 action snapshot 和 decision 的内存审计记录。

这些性质限定在当前 Python 进程、固定 policy 结构和 <code>ExecutionGateway.submit()</code> 入口。调用方可以直接绕过网关修改外部环境，因而 Demo 没有证明 complete mediation。其 ALLOW 结果也只代表已配置检查通过，不包含工具内部鉴权、真实资源状态和执行后条件。

## 8. 主要局限

| 局限 | 当前后果 | 后续验证方向 |
|---|---|---|
| 单动作、无 Agent loop | 无法验证跨步时序、累计次数和状态污染 | 增加 session state 与多步序列 |
| 模拟副作用 | 无法观察真实文件、网络、进程和部分成功 | 使用隔离的 instrumented sink |
| 审批记录可重复使用 | 完全相同的已批准 action 可以再次提交 | 增加 nonce、消费状态和 exactly-once |
| actor/session 来自 action | 没有身份认证，调用方可声明主体 | 从可信执行上下文注入身份 |
| 无签名、过期、撤销 | 审批存储只在 Demo 中被假定可信 | 签名 token、expiry、revocation |
| args 使用 Python 对象相等 | 未定义跨语言规范化和 canonical serialization | 规范化参数后绑定哈希 |
| 路径为词法规范化 | 未解析 symlink、junction、实际挂载和 TOCTOU | 在打开资源时做句柄级 containment |
| schema 类型有限 | 仅支持 string、boolean、integer 和平面参数 | 引入正式 JSON Schema 与嵌套结构 |
| 审计仅在内存 | 进程退出即丢失，且没有防篡改、尾部完整性或脱敏 | 持久事件日志、外部锚定、redaction |
| 无 postcondition | ALLOW 后无法确认真实执行与目标终态 | 记录 tool result 和环境 oracle |
| 无恢复 | DENY 或工具失败后只能结束当前调用 | 加入有界 replan/resume 与再次过 gate |
| 无并发模型 | 未验证重放、竞态和检查—使用时间差 | 并发、重入和 TOCTOU 测试 |

审计记录保存完整 action，参数中若含 secret 或个人信息会直接进入内存日志。后续持久化审计前应先建立字段最小化、脱敏和访问控制规则。

## 9. 可用于后续实验的价值

当前 Demo 已具备确定性、零第三方依赖、场景数据化和 action-sink 可计数四项优势，适合作为报告 12 实验协议的公共夹具。它可以直接承接 SPEC-02/04、CONS-01–04/08、AUTH-01–04/07、MED-01/05/06、VERIFY-02 和 COMPOSE-01/03/06 的简化版本。实验扩展时应保持现有不变量：每个候选动作只从统一 gateway 进入模拟 sink；所有 verdict 均可审计；DENY 在副作用前生效；恢复产生的新动作重新经过同一 gate。

建议按以下顺序扩展：

1. 为 approval 增加 nonce、消费状态、expiry、revocation 和可信 principal。
2. 增加 malformed action/policy、approval store 错误和 audit sink 错误夹具。
3. 引入 session state，测试调用次数、非法顺序和跨步 provenance。
4. 使用临时隔离资源替代内存 effects，加入 symlink、TOCTOU 和部分成功测试。
5. 增加 tool-result postcondition、有界恢复和恢复后再次授权。
6. 将审计改为可关联、持久、可验证且经过脱敏的事件记录。

## 10. 结论

Short Chain Compliance Demo 已经实现一条清楚、可运行、可测试的最小执行控制链。它将 policy、schema、资源范围与审批转换成结构化 verdict，并由统一 gateway 决定模拟副作用是否发生。本轮 7/7 个场景夹具和 12/12 个单元测试均通过，支持“受控入口内的确定性 fail-closed、精确参数审批绑定、DENY 无模拟副作用和全提交审计”这四项局部结论。

当前实现的研究价值主要体现在控制链可观测性和实验可扩展性。生产级保证仍需要补齐可信身份、审批一次性、真实副作用完整调解、跨步状态、postcondition、受约束恢复与持久审计。后续实验应以真实 action sink 和环境终态为判据，并继续区分组件功能存在、受控路径验证和完整 deployable harness 保证。

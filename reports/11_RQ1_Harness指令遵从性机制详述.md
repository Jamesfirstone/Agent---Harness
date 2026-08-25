# RQ1：开源 LLM Agent Harness 指令遵从性代码机制详述

**核验日期：2026-08-25**<br>
**研究问题：**开源 LLM Agent 系统在其 deployable harness 中实现了哪些用于规范、约束、检测、恢复、授权和验证指令执行的代码级控制？这些控制在项目、执行生命周期、保证形式与组合结构上的分布如何？

**证据基础：**[初始代码证据矩阵](01_代码级证据矩阵.md)、[本地验证记录](02_本地验证记录.md)、[初始综合报告](03_初始文献与代码证据综合报告.md)、[补充研究协议](05_补充性系统映射研究协议.md)、[补充综合报告](06_补充性系统映射与代码证据综合报告.md)、[最终定义与代码审查](08_最终Agent指令不遵从定义与Harness代码级审查.md)。

## 摘要

本报告专门回答 RQ1。按照固定提交中的执行入口、裁决所有者和副作用关系进行审计，当前证据支持 21 个运行时或决策层代码实现单元，另有 AgentDojo、HarnessAudit 两个以检测和后置验收为主的实现。21 不是完整 harness 的数量；当前主清单一行对应一个项目中的一条主要实现路径，其中既有真正支配工具或副作用的执行门，也有依赖宿主接线的策略源、审批 middleware、validator、scanner、信息流原型和恢复组件。

这些实现覆盖六类 RQ1 控制：把指令编译为规则、schema 或 contract 的规范控制；在规划、工具和副作用之前做 policy、capability、IFC 或参数检查的约束控制；以 scanner、monitor、trace 和 postcondition 识别违规的检测控制；通过 fallback、resume、reask 或 replan 处理失败的恢复控制；以 allowlist、capability token、approval 和 HITL 管理权限的授权控制；以及通过 schema、工具结果、终态和审计链提供证据的验证控制。

项目之间最重要的差异不是是否使用 “guardrail” 一词，而是 verdict 是否支配真实 action sink。ActPlane 在 Linux/eBPF 副作用点返回 <code>-EPERM</code> 或发送 <code>SIGKILL</code>；Governance Toolkit、OpenAI Agents 和 MCP PEP 的受控路径把裁决接入工具 dispatcher；NeMo 在受控 rail/client tool path 中产生裁决，但真实工具仍由 client harness 执行；Enterprise Harness 在验证失败后以确定性 composer 接管最终输出。相比之下，LlamaFirewall、Agent Policy Guard、Invariant analyzer、Guardrails validator 等组件只有在宿主消费其 verdict 时才成为强制门；AgentDojo 和 HarnessAudit 主要提供 runtime check、终态 oracle 或轨迹评分，不能与事前阻断混写。

分布上，代码控制明显集中在规范化、执行前验证和工具调用边界；系统级副作用拦截、完整的跨步状态、受约束恢复和不可丢失审计更少见。保证形式同时包含 hard block、审批暂停、条件放行、软反馈、隔离和后置检测，并且多标签重叠，不能把行数相加为 21。组合结构常见为 policy→gate→tool、provenance/IFC→authorization→execute、middleware→approval→resume、scanner→caller gate→action sink、sandbox→audit 和 oracle→recovery。当前没有 E4 级独立复现或生产证据，因而结论应理解为代码机制与证据边界的审计，而不是项目安全排行榜。

## 1. RQ1 的直接回答

开源 LLM Agent 项目已经实现了相当丰富的代码级控制原语，但它们分布在不同生命周期位置，也具有不同的执行所有权。

- **规范与编译：**AgentSpec、CUGA、Agent Policy Guard、NeMo、Guardrails AI 和 Enterprise Harness 将自然语言要求转换为规则、policy object、rail、schema、validator 或 contract。
- **执行前约束：**Governance Toolkit、OpenAI Agents、NeMo、AgentSpec、CUGA、MCP PEP、AgentGuard、Google ADK 等在工具调用前进行 schema、policy、approval 或 scanner 判断。
- **权限与信息流：**CaMeL、Fides、PFI、MCP PEP 和 Tool Forge 分别使用可信意图、taint/IFC、capability token、工具卡、session scope 或 sandbox 限制能力与数据流。
- **副作用控制：**ActPlane 把控制下沉到 Linux/eBPF/LSM；Tool Forge 使用容器；其他大多数项目只保护经过指定 wrapper、interpreter、middleware 或 dispatcher 的工具调用。
- **检测和验证：**Guardrails AI、Invariant、LlamaFirewall、AgentDojo、HarnessAudit 以及 NeMo 的 tool-result rail 提供输出、轨迹、工具结果或终态检查。
- **恢复：**Enterprise Harness 的 deterministic fallback、OpenAI Agents/PydanticAI/Microsoft Agent Framework 的暂停与恢复、Guardrails AI 的 reask/fix、ToolSafe 的反馈重规划构成不同强度的恢复路径。
- **审计：**Governance Toolkit、MCP PEP、Tool Forge、HarnessAudit 等记录裁决或轨迹，但已有哈希链仍不能证明不存在未记录的旁路或尾部截断。

这些机制并未在每个项目中形成完整闭环。当前证据最稳定的总体判断是：代码所有权、完整调解、默认与异常语义、审批绑定和旁路覆盖共同决定保证强度；机制名称和机制数量本身不能回答“agent 是否被强制遵从”。

## 2. 操作化定义、证据和计数规则

### 2.1 什么计为代码级控制

本报告用于后续细粒度复核的理论分析单元定义为：

> 项目 + 固定提交 + enforcement owner + entrypoint/decision semantics。

一个单元必须在固定提交中读取消息、计划、工具、参数、主体、状态或结果，并产生验证、变换、暂停、拒绝、隔离、恢复或审计效果。同一 verdict path 的薄 wrapper 应合并，不同执行所有者、不同生命周期位置或独立 verdict 的路径在后续 enforcement-point 级编码中应拆分。本报告现阶段采用项目级主路径清单：一项目一行，共 21 行；因此 21 只能作为已审计实现单元数，不能作为细粒度机制出现次数。

只存在 README、system prompt、论文架构图或未来发布声明的对象不计代码实现。只在运行后评分的 checker 保留为 detector/postcondition 对象，不并入运行时强制分母。策略源、scanner 和 SDK validator 可以进入 21 个决策实现，但必须标记为“宿主依赖”，不得写成完整 harness。

### 2.2 证据等级

| 等级 | 操作定义 | 本报告允许支持的结论 | 不能自动支持的结论 |
|---|---|---|---|
| E0 | 只有文档、提示或论文声称 | 设计意图、术语或候选机制 | 已实现、已接线、可部署 |
| E1 | 固定提交中存在可定位实现路径 | 控制逻辑存在，能够描述入口和分支 | 路径已通过测试或覆盖所有入口 |
| E2 | 有针对性测试，或本地完成局部测试 | 特定路径有测试证据 | 全仓库通过、生产可靠、无旁路 |
| E3 | 行为测量、对照或消融 | 特定实验条件下观察到效果 | 当前 commit 已被本地独立复现 |
| E4 | 独立复现或生产证据 | 在声明范围内有外部复现或部署支持 | 对其他威胁模型和环境普遍成立 |

证据等级描述本轮实际取得的证据，不是项目质量评分。“仓库中有测试文件”与“本地测试通过”分开记录；论文 E3 与本地代码 E1/E2 也分开记录。在本报告当前审计样本中未发现 E4 证据（E4=0）；该结论不能外推为整个开源生态不存在独立复现或生产证据。

### 2.3 分母与排除对象

| 记号或材料 | 数量/状态 | 可用于什么 | 不可用于什么 |
|---|---:|---|---|
| N_impl | 21 | 运行时或决策层代码实现的项目级审计 | 不等于 21 个完整 deployable harness |
| N_det | 2 | AgentDojo、HarnessAudit 的检测/后置验收分析 | 不并入执行强制分母 |
| 初始 manifest | 16 项 | 描述初始材料清单 | 混有 runtime、benchmark、catalog、研究 artifact 和空仓库，不能作 harness 分母 |
| 补充 manifest | 18 项 | 描述 11 个论文仓库与 7 个实践仓库的检出状态 | 不等于最终 21 个实现；3 项存在 partial/case-collision |
| PPT 临时计数 | 10/7/7/6 等 | 作为历史探索线索 | 分母、去重和编码表不可恢复，不能发表为 RQ1 分布 |
| benchmark/evaluator | IFEval、AGENTIF、JSONSchemaBench、τ/τ²-bench | 提供 checker、schema、任务和终态 oracle | 不能写成 deployable runtime gate |
| 不完整代码材料 | Agent-C、TrustAgent、Tangent 等 | 支持论文思想或发布状态说明 | 不计入代码实现分母 |
| 短链 demo | 7 个案例、12 个测试 | 说明一个确定性 gate 的设计方式 | 不证明被调查项目的实现、分布或强保证 |

### 2.4 RQ1 六类动词与 U1–U10 的对应

| RQ1 控制 | 典型可覆盖的 U 类别（非穷尽） | 代码操作定义 | 典型 verdict/effect | 单独不能证明什么 |
|---|---|---|---|---|
| 规范 | U1–U5、U10 | 把要求编译为 schema、DSL、policy、rail、contract 或状态规则 | valid/invalid、规则对象、约束集合 | 规则已覆盖全部真实意图 |
| 约束 | U2–U7、U9 | 在规划、工具或副作用前限制动作、参数、来源、能力或资源 | allow/deny、skip/stop、修改工具集合 | 所有调用入口都经过 gate |
| 检测 | U1–U4、U7–U10 | scanner、monitor、trace checker、postcondition 识别违规 | finding、score、block signal、violation | 已阻止或撤销副作用 |
| 恢复 | U8、U10 | fallback、resume、reask、fix、replan、补偿或终止 | composer、retry、resume、feedback | 恢复后的新动作仍然安全 |
| 授权 | U4–U7、U9 | allowlist、capability、approval、HITL、session scope | allow/deny/ask/pending | 审批绑定了精确主体、参数和资源 |
| 验证 | U1–U3、U8–U10 | schema、tool-result、环境 oracle、audit 验证输出或轨迹 | pass/fail、postcondition、hash record | 事前阻断、日志完整或无旁路 |

U1–U10 描述指令不遵从的结果空间，机制族描述代码控制的位置与所有者；二者是多对多关系，不能从某个机制反推其完整覆盖某个 U 类别。U1–U10 的定义来源见报告 08 第 2.2 节。U1–U10、机制族、生命周期和保证形式均为多标签。同一实现可以同时规范、授权、验证并恢复，因此标签出现次数不能相加得到 21。表中的 “未观察到” 始终表示 “在已检查路径中未观察到”，不表示机制不存在。

## 3. 21 个运行时或决策层实现总矩阵

| ID | 项目与固定提交 | 主要机制 | 主要生命周期 | 保证形式 | 默认/异常与主要旁路 | 证据 |
|---|---|---|---|---|---|---|
| I01 | ActPlane <code>47cd96c</code> | eBPF/LSM 文件、网络、进程副作用拦截 | 执行中/副作用点 | hard block、isolation | 无匹配放行；hook 外 API、非 Linux 环境 | E2-source；E3-paper |
| I02 | Microsoft Agent Governance Toolkit <code>81955d4</code> | policy、verdict、HITL、audit | 执行前、审批、恢复、审计 | deny、pause/resume | no-match/backend error deny；warn/log permit；dispatcher 外旁路 | E2-source |
| I03 | Enterprise LLM Agent Harness <code>e8e60fb</code> | contract、schema、deterministic fallback | 输出验证、恢复 | code-owned fallback | prompt-only 检出后仍返回；不回滚外部副作用 | E2-local-partial；E3-paper/comparison |
| I04 | OpenAI Agents Python <code>5250cb8</code> | strict schema、tool guardrail、approval/resume | 执行前、工具边界、恢复 | reject、pause/resume | raw callable 绕过；审批可显式关闭 | E2-source |
| I05 | NVIDIA NeMo Guardrails <code>1c657ca</code> | input/output/tool-call/tool-result rails | 输入、执行前、执行后 | conditional block | 普通 rail 异常 unsafe；HTTP 异常 re-raise；disabled/空 rail 放行 | E2-source |
| P01 | AgentSpec <code>e6fa390</code> | trigger–predicate–enforcement DSL | 规范、规划、执行前 | continue/skip/stop/self-reflect | 无匹配 pass-through；executor 外直调 | E1 |
| P02 | CaMeL <code>f083b6b</code> | security policy、interpreter、privileged path；trusted/quarantined/IFC 为论文架构概念 | 规划、信息流、工具前 | policy deny/confinement | 正常无匹配拒绝；NoSecurityPolicyEngine 永久允许；interpreter 外旁路 | E1-local-code；E3-paper |
| P03 | Fides <code>669c046</code> | confidentiality/integrity label、PolicyViolation | 工具结果、下一工具前 | IFC block | notebook 原型；BasicPlanner 可绕过 labeled loop | E1 |
| P04 | PFI <code>73ee2b5</code> | trusted/untrusted agent、data-flow/provenance；HITL 仅作论文/架构参照 | 来源标记、规划、sink 前 | conditional control | 默认 UNSAFE_DATAFLOW_YES；exec 失败回退 LLM | E1-local-code；E3-paper |
| P05 | CUGA <code>8b45234</code> | intent guard、playbook、tool guard、approval | 规划、工具前、输出后 | block/modify/approval | policies 默认关闭；catch-all、未初始化、target mismatch 可继续 | E2-source，未本地运行 |
| P06 | Tool Forge <code>07947e9</code> | tool card、release/session allowlist、container sandbox | 注册、路由、执行 | capability reduction、isolation | unpublished/local owner/dynamic import 边界 | E2-source，未本地运行 |
| P07 | MCP PEP <code>3dd9690</code> | PEP、capability、IFC、limit、hash audit | 工具前、执行、审计 | 只有 ALLOW 执行 | 无规则默认 allow；skip_pep；确认 UI 未闭合 | E1 + E2-local-partial |
| P08 | AgentGuard <code>20d4af5</code> | enforcer、adapter、远程/本地 guard | attach、工具前 | middleware gate | 可配置 fail_open；未 attach 或直调绕过 | E2-source，未本地运行 |
| S01 | Google ADK <code>c986ff0</code> | FunctionTool confirmation、plugin hook | 工具前、审批 | optional pause | 默认不要求确认；raw callable、非 FunctionTool 旁路 | E2-source，未本地运行 |
| S02 | Microsoft Agent Framework <code>435201b</code> | session approval middleware、resume、standing rule | 审批、恢复 | pause/resume | middleware opt-in；tool-name 自动批准碰撞面 | E2-source，未本地运行 |
| S03 | PydanticAI <code>97f2114</code> | deferred ApprovalRequired、history/resume | 工具前、审批、恢复 | pause/resume | 默认不审批；客户端可伪造 history；直调旁路 | E1 Git-object + E2-not-run |
| S04 | Guardrails AI <code>c472d55</code> | validator、reask/fix/filter/refrain/exception | 输入/输出验证、恢复 | soft feedback 或 stop | 路径间 EXCEPTION/NOOP 不一致；绕过 Guard wrapper | E1 + E2-source |
| S05 | Invariant <code>2340fe2</code> | analyzer、Monitor | 检测、工具前可选、审计 | finding 或 raise | analyze 结果可被忽略；Monitor 外路径 | E2-source，未本地运行 |
| S06 | Agent Policy Guard <code>6702e0b</code> | YAML allow/deny/ask/HITL effect | policy、工具前、审批 | host-dependent decision | engine 只返回 effect；宿主忽略即无保护 | E1 + E2-not-run |
| S07 | LlamaFirewall <code>e36f132</code> | scanner、BLOCK/HITL、replay、CodeShield | 输入、工具前、轨迹 | block signal、HITL | 空 scanner、缺 trace、ALLOW+ERROR、caller 忽略 | E2-source；补充 manifest 外参照 |
| S08 | ToolSafe <code>46358fa</code> | step guard、alignment、security feedback/replan | 规划、工具前、恢复 | hard block 或 soft replan | known_actions/parser 覆盖有限；模型介导恢复；partial/case-collided | E1-local-code；E3-paper |

这张矩阵是 RQ1 的主索引，而不是排名。I、P、S 三组表示报告组织方式：I 组具有较清楚的在线执行所有权或代码拥有恢复；P 组强调策略、能力、信息流或工具 gate；S 组强调 SDK、审批、validator 和策略信号。分组不是互斥保证等级。

P01–P08 与 S01–S08 是机制卡片集合，不是补充仓库全集。补充仓库全集以 <code>repos/supplement/manifest.json</code> 的 18 个固定 commit 为分母，其中 15 个完整、3 个 partial/case-collided；LlamaFirewall 是 manifest 外的交叉代码参照。Agent-C 虽标记 complete，但只有 README；TrustAgent 有 322 个 tracked path 无法在当前 Windows 工作树检出，工作树为 0 文件；PydanticAI 有 2535 个 tracked path 未完整恢复，证据来自 immutable Git object；ToolSafe 为 partial/case-collided。三类对象不得相互替代计数。

### 3.1 代码锚点、执行所有者与部署类别

| ID | 代表代码锚点 | Enforcement owner | 部署类别 |
|---|---|---|---|
| I01 | <code>policies/readonly.yaml:7-12</code>；<code>bpf/process.bpf.c:1763-1780</code> | eBPF/LSM hook | 系统级副作用拦截器 |
| I02 | <code>policy.ts:450-551</code>；<code>runtime.rs:160,337</code> | policy engine + governance dispatcher | runtime harness |
| I03 | <code>server/index.mjs:1020-1164</code>；<code>guardrail.mjs:30-55</code> | response/composer path | 输出层 harness/fallback |
| I04 | <code>function_schema.py:23,473</code>；<code>tool_execution.py:1785-1990</code> | SDK tool dispatcher | SDK runtime gate |
| I05 | <code>rails_manager.py:327-429</code>；<code>tool_call_action.py:38-59</code> | rails manager + client harness | 宿主依赖 rail |
| P01 | <code>controlled_agent_excector.py:82-99,164</code>；<code>enforcement.py:31-85</code> | controlled executor | 研究型执行器 |
| P02 | <code>security_policy.py:58-110</code>；<code>interpreter.py:2048-2065</code> | policy engine + interpreter | 研究型 interpreter |
| P03 | <code>Tutorial.ipynb:1483,1495-1519,1533</code> | labeled planning loop | notebook 原型 |
| P04 | <code>pfi_agent_creation.py:55-67,228-296</code>；<code>pfi_tools.py:70-117</code> | PFI agent/tool path | 研究型信息流组件 |
| P05 | <code>policy/enactment.py:32-120</code>；<code>tool_guard_runtime.py:761-874</code> | CUGA graph/policy runtime | 宿主 runtime 组件 |
| P06 | <code>tool_router.py:423-572</code>；<code>container_sandbox.py:13-50</code> | scoped router + sandbox | 工具平台/隔离组件 |
| P07 | <code>pep/enforcer.py:103-306</code>；<code>agent_runner.py:346-371</code> | PEP + agent runner | 可部署原型 |
| P08 | <code>enforcer.py:29,59,95-148</code>；<code>compat.py:45-100</code> | attached adapter/enforcer | 宿主依赖 middleware |
| S01 | <code>function_tool.py:99-142,291-353</code>；<code>functions.py:783-947</code> | FunctionTool/flow | opt-in SDK 控制 |
| S02 | <code>_tool_approval.py:343,355-640</code> | approval middleware | opt-in SDK 控制 |
| S03 | <code>tools.py:306,333,431,506</code>；<code>_deferred.py:27-187</code> | deferred tool runner | partial checkout / SDK |
| S04 | <code>guard.py:86,252-272,485-510</code>；<code>validator_base.py:102-155</code> | Guard wrapper | 验证库组件 |
| S05 | <code>policy.py:23,77-126</code>；<code>monitor.py:78,141-175</code> | caller or Monitor | 决策/监控组件 |
| S06 | <code>models.py:10-37,93-120</code>；<code>engine.py:54,117-161</code> | policy engine，最终 owner 为 host | 策略源组件 |
| S07 | <code>llamafirewall.py:108-187</code>；<code>alignmentcheck_scanner.py:74-130</code> | scanner caller | manifest 外决策组件 |
| S08 | <code>sec_react_agent.py:73-124</code>；<code>react_firewall_agent.py:70-103</code> | guarded agent loop | partial/case-collided 研究原型 |

## 4. 直接在线强制与代码拥有恢复

### 4.1 ActPlane：副作用点的系统级拦截

ActPlane 的策略入口包括 <code>policies/readonly.yaml:7-12</code>，内核路径位于 <code>bpf/process.bpf.c:1763-1780,2413-2449</code>，端到端材料位于 <code>script/e2e_examples.sh:107-160</code> 和 <code>test/e2e_cases.yaml:137-144</code>。当文件、网络或进程操作命中 eBPF/LSM 策略时，内核可返回 <code>-EPERM</code> 或发送 <code>SIGKILL</code>。这使控制不依赖模型是否理解或服从规则，而是直接接近真实副作用。

其保证仍有明确边界：无匹配规则时放行；未挂载 hook、非 Linux/eBPF 环境、外部 SaaS/API 或未覆盖的 sink 不在同一保证内；<code>SIGKILL</code> 也可能晚于部分副作用。ActPlane 提供拒绝和隔离，不等于应用层 rollback、补偿或安全重规划。代码与测试为 E2，论文性能/行为测量单列为 E3。

### 4.2 Governance Toolkit：策略、审批、执行与审计

主要锚点为 <code>agent-governance-typescript/src/policy.ts:450-551</code>、<code>policy-engine/core/src/runtime.rs:160,337</code>、<code>policy-engine/core/src/verdict.rs:100,229</code>、审批测试 <code>test_human_approval.py:74-101</code> 和 <code>audit.ts:14-95</code>。策略在工具执行前求值并正规化为 verdict；无匹配和后端错误默认 deny；审批拒绝不执行，批准后恰好执行一次。由此形成 policy→approval→dispatch→audit 的在线链。

但 <code>warn/log</code> verdict 仍 permit，extractor 异常可能被吞掉，绕过治理 dispatcher 的工具也不受保护。审批路径证明的是暂停和单次恢复，不是已经发生的外部副作用回滚。证据为 E2。

### 4.3 Enterprise Harness：验证失败后的代码拥有输出恢复

核心代码位于 <code>server/index.mjs:1020-1164</code>、<code>server/guardrail.mjs:30-55</code>，测试见 <code>tests/harness.test.mjs:104-135</code> 和 <code>tests/guardrail-scorer.test.mjs:93-150</code>。最关键的对照是：prompt-only 分支记录 violation 后仍返回模型原输出，而 code-owned 分支在验证失败时进入确定性 composer；external guardrail 则产生 pass/redact/refuse 等结果。

因此，是否“检测到违规”不是核心，最终返回权属于谁才是核心。composer 能控制输出层恢复，但不能自动撤回邮件、支付或数据库操作。本地 guardrail 核心测试 23/23，通过范围明确；全量测试为 25/34，不能写成完整本地复现。论文/对照为 E3，本地证据仍需限定。

### 4.4 OpenAI Agents Python：schema、guardrail 与审批恢复

主要锚点为 <code>function_schema.py:23,473</code>、<code>tool.py:417-420,441,480,483,486,595</code>、<code>tool_execution.py:1785-1838,1858-1990</code>，恢复测试见 <code>test_run_impl_resume_paths.py:421-460</code> 和 <code>test_hitl_session_scenario.py:128-180</code>。pending approval 时工具不执行；批准后 run 恢复；拒绝产生 rejection；工具输入/输出 guardrail 可以拒绝或抛错。

源码同时明确记录直接包装 callable 可能绕过 schema、guardrail、timeout 和 tracing，<code>needs_approval=False</code> 也会关闭审批。因而保证只覆盖进入框架 dispatcher 的工具。暂停—批准—恢复属于状态恢复，而不是任意外部副作用回滚。证据为 E2。

### 4.5 NeMo Guardrails：输入、工具调用与工具结果的多阶段 rail

主要锚点为 <code>rails_manager.py:327-429</code>、<code>tool_call_action.py:38-59</code>、<code>tool_result_action.py:50-162</code> 和 <code>tool_rail_action.py:37-63</code>。malformed tool call、非法参数、工具名或调用 ID 不一致以及普通 rail 异常可进入不安全路径。它不仅检查输出文本，也检查工具调用和结果的关联。

失败语义并不统一：普通 rail 异常通常被视为不安全，上游 HTTP 状态异常会继续抛出；无 active rail、<code>enabled=False</code>、空调用或空结果可以 pass。真实工具仍由 client harness 执行，因此绕过 manager 或关闭 rail 会失去保护。证据为 E2。

## 5. 策略、能力、信息流与工具 Gate

### 5.1 AgentSpec

<code>controlled_agent_excector.py:82-99,164</code>、<code>enforcement.py:31-85</code> 和 <code>interpreter.py:112-139</code> 把 trigger–predicate–enforcement 规则转成 <code>CONTINUE/SKIP/STOP/SELF_REFLECT</code>。它保护候选动作和执行状态，位置在受控 executor 的工具执行之前。无匹配规则 pass-through；直接调用工具或绕开 executor 会失去规则所有权。<code>SELF_REFLECT</code> 是局部重新评估，不证明环境回滚或补偿。E1。

### 5.2 CaMeL

<code>security_policy.py:58-110</code>、<code>interpreter.py:2048-2065</code> 和 <code>privileged_llm.py:459-474</code> 将可信意图、控制流、数据流和特权动作分离。真实策略路径对不允许的私有数据流或无匹配规则拒绝，但显式 <code>NoSecurityPolicyEngine</code> 永久允许；只有经 CaMeL interpreter 发出的动作受保护。该机制比内容扫描更接近来源与权限模型，但 metadata/source adapter 的完整性决定保证。E1，论文行为证据另列 E3。

### 5.3 Fides

Fides 的可核证路径主要位于 <code>Tutorial.ipynb:1483,1495-1519,1533</code>。<code>LabeledPlanningLoop</code> 对 confidentiality/integrity 标签做 join，并在下一工具或 sink 前抛出 <code>PolicyViolation</code>；未知工具趋向 closed。其主要限制是 notebook 原型和可绕过 labeled loop 的 <code>BasicPlanner</code>。E1。

### 5.4 PFI

<code>pfi_agent_creation.py:55-67,228-296,1014-1080</code>、<code>config.py:5-21</code> 和 <code>pfi_tools.py:70-117</code> 将输入、agent 与工具流划分为 trusted/untrusted。未知输入降级为 untrusted，但默认 <code>UNSAFE_DATAFLOW_YES</code> 允许不安全流，条件 <code>exec</code> 失败还可能回退 LLM。因此它具有来源与信息流表达力，却不能按默认配置描述为硬拒绝。E1，论文测量 E3。

### 5.5 CUGA

<code>policy/models.py:9-31,279-307</code>、<code>policy/enactment.py:32-120,228-233</code> 和 <code>tool_guard_runtime.py:761-874</code> 组合 Intent Guard、Playbook、Tool Guide/Guard、Tool Approval 和 Output Formatter。<code>BLOCK_INTENT</code> 可在规划前拒绝，<code>MODIFY_TOOLS</code> 收缩工具空间，tool guard 和 approval 位于工具前。

其覆盖很宽，但默认 <code>enable_policies=False</code>，顶层 catch-all 可能记录后继续无策略执行，未初始化、无 guard 或 <code>target_apps</code> 不匹配也可能放行。恢复或 playbook 重新规划后的动作是否再次进入同一 gate，需要单独验证。E2。

### 5.6 Tool Forge

<code>tool_card_schema.py:318-383</code>、<code>tool_router.py:423-572,682-704,998-1024</code>、<code>container_sandbox.py:13-50</code> 将工具卡、发布状态、session allowlist、路由和容器隔离连接起来。它缩小 agent 可见与可执行的能力面，并在 sandbox 内执行工具。card、release、session 和 sandbox 错误多为 closed。

部署边界包括 <code>include_unpublished=True</code>、默认 local-owner、dynamic import 和任何绕过 scoped router 的 callable。该项目更像工具供应链与隔离控制，而不是完整的用户指令语义验证器。E2。

### 5.7 MCP PEP

<code>prototype/pep/enforcer.py:103-306</code>、<code>rules.py:27-85,134-165</code>、<code>audit/logger.py:68-172</code> 和 <code>agent_runner.py:346-371</code> 把结构化工具调用接入 PEP。工具、typed args、capability token、调用次数以及 SI/DS/intent-taint 共同进入裁决；只有 <code>ALLOW</code> 才执行，token、limit 和 <code>DENY</code> 为 closed，并记录哈希审计。

重要边界是无规则默认 allow、<code>skip_pep</code> 显式旁路，以及 <code>REQUIRE_CONFIRM</code> 尚无完整审批 UI。本地 42 项测试中 39 项通过、1 项失败、2 项错误；两个错误来自 Windows symlink 权限，失败来自 POSIX 路径假设。intent-taint、IFC、filesystem-prefix 和非 symlink containment 路径通过。该结果支持局部 E2，不证明完整 PEP 闭环。

### 5.8 AgentGuard

<code>enforcer.py:29,59,95-111,136-148</code> 和 <code>compat.py:45,57,96-100</code> 通过 adapter 把远程或本地 guard 接到工具调用前。保护只在 attach 后成立；远程不可用时可以配置 <code>fail_open</code>，未 attach、直接调用原始工具或未适配 provider 都会绕过。仓库有针对 adapter 的测试代码，但本地未统一运行，故记 E2 源码/测试证据而非本地全量通过。

## 6. SDK、审批、输出验证器与策略源

### 6.1 Google ADK

Google ADK 的 <code>FunctionTool</code> confirmation 和 plugin callback 在工具分发前提供可选审批。只有工具按预期封装并启用确认时，pending 状态才会阻止执行；默认不要求确认。raw callable、非 <code>FunctionTool</code> 和未经过 plugin 生命周期的路径可绕过。当前材料未证明审批完整绑定唯一工具、精确参数、主体、资源、session、expiry 和撤销状态。E2。

### 6.2 Microsoft Agent Framework

session approval middleware 保存 pending/approved/denied 状态，并支持 resume 和 standing rule。它比一次性布尔确认更接近审批工作流，但 middleware 是 opt-in。按工具名自动批准可能发生同名工具或参数变化的碰撞；middleware 外 callable 不受保护。E2。

### 6.3 PydanticAI

deferred <code>ApprovalRequired</code> 暂停工具执行，并通过 <code>DeferredToolResults</code> 或历史状态恢复。默认工具不需要审批；官方材料明确提醒不可信客户端可能伪造 history/approval，敏感工具仍需内部鉴权。因此该机制解决 pause/resume，不自动构成可信 authorization boundary。证据来自 immutable Git object、源码和测试材料，当前未本地运行。E2 源码/测试。

### 6.4 Guardrails AI

validator 可产生 reask、fix、filter、refrain、exception 等路径，覆盖结构验证、检测和局部恢复。部分异常路径可以 closed，但不同入口可能映射为 <code>NOOP</code>；绕过 <code>Guard</code> wrapper、直接调用 provider 或工具时无保护。输出 validator 也不能撤销已经发生的外部副作用。E1–E2。

### 6.5 Invariant

<code>LocalPolicy.analyze</code> 返回 finding，调用方忽略即继续；<code>Monitor.run</code> 对未处理违规可抛错。因而同一项目中 analyzer 应编码为检测器，Monitor 在位于 action sink 前且异常不被吞掉时才是条件性 runtime gate。当前固定提交不能外推为完整 Gateway。E2。

### 6.6 Agent Policy Guard

YAML policy engine 返回 allow/deny/ask/HITL effect；默认无匹配为 ask。engine 本身不负责 tool dispatch，宿主必须把 <code>DENY</code> 转成停止，把 <code>ASK/HITL</code> 转成暂停。若宿主忽略 effect 或存在未接入 policy 的 direct tool，规则不产生执行效果。源码与测试存在，但本地缺少 pytest，未运行。E2 源码/测试。

### 6.7 LlamaFirewall

scanner pipeline 产生 ALLOW、BLOCK、HITL、ERROR，replay 和 CodeShield 提供轨迹或代码检查。BLOCK/HITL 可以使 scanner pipeline 短路，但 HITL 只是 signal，不是内置审批系统；空 scanner、缺 trace、部分 ALLOW+ERROR 和 CodeShield <code>IGNORE</code> 路径偏 open。只有 caller 把 verdict 接到 dispatcher，才形成 execution control。E2。

### 6.8 ToolSafe

step-level alignment guard 在判断 false 时可以不执行工具；security reaction 则把风险反馈给模型并依赖重新规划，属于软恢复。<code>known_actions</code> 和 parser 决定哪些动作可见，未识别动作不能自动视为安全。硬阻断路径与论文 E3 行为材料分开记录；代码为 E1。

### 6.9 Approval 绑定标准

approval 要升级为授权，至少应绑定：

> principal × session × unique tool identity × normalized args × resource scope × expiry × revocation × unforgeable approval/resume token。

当前项目普遍证明了“可以插入审批点”，但没有普遍证明该元组完整实现。tool-name-only approval、客户端历史、可重放 resume、未区分资源范围的 standing rule，以及 HITL 只返回 signal 都会削弱授权保证。工具内部的最终鉴权仍不可省略。

## 7. 检测与执行强制必须分开

| 对象 | 观察点 | 是否支配后续动作 | 默认/边界 | 本报告编码 |
|---|---|---|---|---|
| AgentDojo <code>089ed46</code> | 未注册工具、参数、注入、utility/security 终态 | 局部 runtime 可拒绝；终态 oracle 不支配已发生副作用 | <code>raise_on_error=False</code> 可把工具错误变成 observation；detector 配置依赖 | D01，N_det |
| HarnessAudit <code>6317162</code> | boundary、fidelity、stability、completion、action sink trace | 主要评分与审计，不自动阻断 | 无匹配 allow；completion 失败只影响评分；sink 外动作不可见 | D02，N_det |
| IFEval/AGENTIF | 文本约束和 CSR/ISR | 否 | 执行后 checker | benchmark，不计 N_det |
| JSONSchemaBench | JSON/schema 实例 | 否 | 结构验证 benchmark | benchmark，不计 N_det |
| τ-bench/τ²-bench | 业务规则、数据库终态、任务奖励 | 规则多为 prompt specification；终态是 post-hoc | 已发生副作用不可撤回 | benchmark，不计 N_det |

AgentDojo 的 <code>functions_runtime.py:246-310</code> 可识别未注册工具或非法参数，显式注入 detector 可以 abort；但任务 checker 主要给出 benchmark 结果，默认工具错误还可能继续。HarnessAudit 的 <code>checker.py</code>、<code>completion_checks.py</code> 和 <code>action_sink.py</code> 检查完整轨迹，但默认无匹配 allow，completion 失败不是运行时阻断。

因此，检测结果只有被转换成 block、approval、isolation、rollback、replan 或 termination，并且该状态转换发生在 action sink 前，才从“发现不遵从”升级为“约束不遵从”。

## 8. 四个分布轴

### 8.1 项目分布

| 项目组 | IDs | 控制所有者 | 可回答的分布事实 | 主要保留意见 |
|---|---|---|---|---|
| 直接在线强制/代码拥有恢复 | I01–I05 | OS hook、runtime gate、dispatcher、rail、composer | 5 个项目具有较清楚的在线执行或最终返回所有权 | 仍存在 hook、dispatcher、client 或 prompt-only 旁路 |
| 策略/能力/IFC/工具 gate | P01–P08 | policy engine、interpreter、router、PEP、adapter | 8 个项目实现规范、来源、能力、隔离或工具前门 | 多数依赖受控 interpreter、配置或 attach |
| SDK/审批/validator/策略源 | S01–S08 | middleware、validator、scanner、approval state | 8 个项目提供可复用治理组件 | verdict 常依赖宿主消费，不等于完整 harness |
| 检测/后置验收 | D01–D02 | runtime checker、trace/action sink | 2 个实现补足终态与轨迹证据 | 不并入 21 个执行/决策实现 |

项目分布显示，组件型实现多于系统级副作用控制。21 个实现覆盖广泛，但不能解释为 21 个完整、不可绕过的 harness。

### 8.2 生命周期分布

| 生命周期阶段 | 代表 IDs | 常见机制 | 共同缺口 |
|---|---|---|---|
| 指令/意图规范化 | I03、P01–P05、S04、S06 | schema、DSL、contract、policy | 规范完整性与自然语言漏编译 |
| 规划与工具选择 | P01–P05、S08 | policy、IFC、tool modification、step guard | 新计划可能从未受控入口执行 |
| 执行前验证 | I02–I05、P05–P08、S01–S08 | schema、policy、scanner、adapter、approval | no-match、异常、默认和 wrapper 旁路 |
| 审批/HITL | I02、I04、P05、P07、S01–S03、S06–S07 | pending、ask、approval、resume | 主体/参数/资源/过期绑定不足 |
| dispatch/真实执行 | I01–I02、I05、P06–P08 | OS hook、dispatcher、sandbox、PEP | direct callable、provider、hook 外 sink |
| postcondition/结果验证 | I03、I05、S04–S05、S07、D01–D02 | tool-result rail、validator、oracle、trace | 往往发生在不可逆副作用之后 |
| 恢复/replan | I03–I04、S02–S04、S08 | fallback、resume、reask、feedback | 新动作是否再次授权和审计 |
| 审计/provenance | I02、P06–P08、S05、S07、D02 | audit、hash、trace | 未记录旁路、尾部截断和 sink 覆盖 |

以下 ID 是代表性覆盖，不是完整闭集；生命周期采用 multi-label，不能按行求和。分布的主要不对称是：规范和执行前控制最丰富，跨步状态、真实副作用拦截、后置验证后的安全恢复以及不可丢失审计相对薄弱。

### 8.3 保证形式分布

| 保证形式 | 操作定义 | 代表 IDs | 是否可直接阻止副作用 | 主要风险 |
|---|---|---|---|---|
| Hard block | verdict 直接禁止 action | I01、I02、I04、P07、部分 S08 | 在受控入口内可以 | hook/gate 外调用、规则遗漏 |
| Pause/approval | action 进入 pending，批准后恢复 | I02、I04、P05、P07、S01–S03、S06–S07 | 正确接线时可以暂停 | signal 未消费、审批绑定过粗 |
| Conditional continuation | 依据配置、规则或错误分支继续 | I03、I05、P01–P05、P08、S01、S03、S06–S07 | 取决于默认和异常语义 | fail-open、no-match allow、空配置 |
| Soft feedback/replan | 把风险反馈给模型或重新生成 | I03、S04、S08 | 通常不能独立保证 | 模型忽略反馈，新动作绕过 gate |
| Semantic/IFC confinement | 通过来源、标签或 capability 限制控制流和数据流 | P02–P04、P07 | 只有最终 gate 消费标签时可以 | 标签传播中断、interpreter/adapter 外路径 |
| OS/container isolation | 在系统或容器边界限制能力 | I01、P06 | 对覆盖的 sink 较强 | sandbox、hook、平台外路径 |
| Post-hoc detection | 执行后发现输出、结果或轨迹违规 | S05、S07、D01–D02 | 通常不能 | 已发生副作用、只评分或记录 |

这些保证形式是多标签。例如一个调用可以先审批、再由 sandbox 执行、最后由 postcondition 检查。表中各行不能相加为 21，也不能据此计算未经预注册编码规则的百分比。

### 8.4 组合结构分布

| 组合模式 | 控制链 | 代表 IDs | 主要断点 |
|---|---|---|---|
| Policy → Gate → Tool | policy effect→dispatcher→tool | P01、P05、P07、S06 | host 忽略 effect、备用 dispatcher |
| Provenance/IFC → Authorization → Execute | label/capability→policy→sink | P02–P04、P07 | 标签传播中断、adapter 外调用 |
| Middleware → Approval → Resume | wrapper→pending→approval→execute | I02、I04、S01–S03 | middleware 外路径、伪造历史、批准碰撞 |
| Scanner/Validator → Caller Gate → Action Sink | verdict→caller→tool/output | I05、S04–S07 | verdict 被忽略、错误转 allow、调用顺序错误 |
| Sandbox/OS Interception → Audit | isolated execution→decision record | I01、P06、I02 | 未经 sandbox 的入口、审计不完整 |
| Adapter/Enforcer → Runtime Gate → Tool | attach/wrapper→verdict→tool | P08、S01、S05–S06 | 未 attach、verdict 被忽略、异常被吞 |
| Oracle/Postcondition → Score/Feedback | result/trace→checker→score/finding | S05、S07、D01–D02 | 只评分或记录，不等于 runtime recovery |
| Postcondition → Constrained Recovery | violation→fallback/resume/reask/replan→再次过 gate | I03、S02–S04、S08 | 恢复动作未重新授权或审计 |

detector 结果只有被宿主转换为 deny、pause、rollback、replan 或 termination，才成为执行控制。组合结构说明，单个机制的局部正确性不足以推断系统保证。真正决定结果的是 verdict owner、节点顺序、状态传播和 action sink 是否被完整调解。

## 9. 机制—生命周期组合图

~~~mermaid
flowchart LR
  A[Instruction / Intent]
  B[Normalize / Spec / Schema]
  C[Plan / Select Tool]
  D[Policy / Capability / IFC]
  E[Approval / HITL]
  F[Unified Dispatch Gate]
  G[Sandbox / OS Interception]
  H[Tool Execution]
  I[Postcondition / Result Validation]
  J[Constrained Recovery / Replan / Resume]
  K[Audit / Provenance]
  L[AgentDojo / HarnessAudit]

  A --> B --> C --> D --> E --> F --> G --> H --> I
  I --> J --> C
  D --> K
  E --> K
  F --> K
  H --> K
  I --> K
  J --> K
  D -. host-dependent decision .-> F
  E -. signal-only risk .-> F
  C -. raw callable / plugin / provider bypass .-> H
  L -. observation / scoring .-> I
~~~

实线表示理想执行链，虚线表示宿主依赖、仅提供信号或旁路。只有 verdict 能支配 <code>F → G/H</code>，并且所有真实副作用入口都经过该路径时，机制才适合称为 runtime enforcement。检测器可以补足 I 阶段，但不会自动撤销 H 阶段已经发生的副作用。

## 10. 默认、异常、恢复和旁路的横向结论

### 10.1 默认配置决定安装后的真实保护

PFI 默认允许不安全数据流，Google ADK 与 PydanticAI 默认不要求审批，Microsoft Agent Framework 的 middleware 是 opt-in，CUGA 可以在政策未启用或异常时继续，MCP PEP 无规则默认 allow，LlamaFirewall 空 scanner 或缺 trace 时可能开放。报告因而必须分别记录“机制存在”和“默认执行生效”。

### 10.2 异常语义必须逐路径核验

NeMo 的普通 rail 异常与 HTTP 异常不同；Governance Toolkit 的 backend error 与 extractor 异常不同；Guardrails 的 EXCEPTION 与 NOOP 路径不同；AgentGuard 远程不可用时可选 fail-open。不能用“项目 fail-closed”概括整个代码库，只能对已定位的分支下结论。

### 10.3 恢复不能脱离原 gate

Enterprise 的 deterministic composer、OpenAI/Pydantic/Microsoft 的 resume、Guardrails 的 reask/fix 和 ToolSafe 的 replan 解决不同层面的失败。可靠恢复至少要求：恢复状态不可伪造；新的动作再次经过 policy、approval 和 sandbox；重试有界；已发生副作用有 rollback 或 compensation；恢复事件进入审计。当前材料没有证明任何一个项目完整覆盖全部条件。

### 10.4 Complete mediation 的常见旁路

- direct/raw callable；
- interpreter、planner 或 labeled loop 外工具；
- plugin、provider、client 或 middleware 外调用；
- 未 attach 的 adapter；
- <code>skip_pep</code>、NoSecurityPolicyEngine、disabled/empty rail；
- dynamic import、unpublished/local-owner 工具；
- 未识别 action/parser fallback；
- action sink、sandbox 或 OS hook 外部副作用。

这些旁路不是在证明项目必然不安全，而是在界定当前代码证据能够支持的保证范围。

## 11. 本地验证账本

| 对象 | 本地状态 | 可以支持的结论 | 不能支持的结论 |
|---|---|---|---|
| Enterprise Harness 核心 guardrail | 23/23 passed | 核心 detector/guardrail/scorer 路径在本地快照通过 | 全仓库通过 |
| Enterprise Harness 全量 | 25/34 passed，9 failed | 当前快照存在 collector/ablation 与 endpoint 差异 | 完整独立复现或 E4 |
| MCP PEP | 39/42 passed，1 failed，2 errors | intent-taint、IFC、filesystem-prefix 等局部路径通过 | 全平台完整 PEP 保证 |
| MCP PEP 两个 error | Windows 缺 symlink privilege | 环境权限造成测试错误 | 机制逻辑失败 |
| MCP PEP 一个 failure | POSIX <code>/etc/passwd</code> 路径假设 | 路径规范化存在跨平台差异 | 所有 containment 检查失败 |
| Agent Policy Guard | 有源码/测试，未运行 pytest | 可标 E2 源码/测试存在 | 本地测试通过 |
| PydanticAI | Git object 中有源码/测试，未本地运行 | 固定 HEAD 路径可审计 | 本地复现 |
| IFEval | 缺 <code>absl</code>，未进入测试 | 环境依赖未满足 | 测试失败或通过 |
| JSONSchemaBench | 缺 <code>dacite</code>，导入失败 | 环境依赖未满足 | 运行时复现完成 |
| Tangent | 无 commit、0 tracked files | 公开 artifact 状态可记录 | 代码级实现存在 |

## 12. 与短链 Demo 的关系

<code>demos/short_chain_compliance</code> 展示候选动作→确定性检测→审计→只在 ALLOW 时追加内存副作用的短链。它覆盖 U2、U3、U4、U6、U9，包含 7 个简单案例和 12 个测试。该 demo 有两个用途：把 scanner/verdict/dispatcher/action sink 的区别变成可运行示例；为后续构造不同 fail-open/fail-closed、approval 和 bypass 测试提供骨架。

它不进入 N_impl 或 N_det，也不作为跨项目分布证据。demo 不覆盖长链状态、真实外部副作用、provenance 传播、postcondition、rollback、签名、过期、撤销或持久审计，更不能支持 E4。

## 13. 对 RQ1 的六条结论

### 13.1 机制数量不等于有效保护

代码库中已经存在 policy、schema、approval、scanner、IFC、sandbox、postcondition 和 recovery，但只有执行所有者能够使 verdict 改变真实行为。完整调解比“项目包含多少机制”更重要。

### 13.2 默认和异常语义决定真实保证

no-match、空配置、解析错误、服务不可用、超时和异常吞掉会让相同机制在不同部署中表现为 deny、pause、warn、raise 或 allow。保证必须绑定到具体分支，而不是项目名称。

### 13.3 Approval 是流程，不自动等于授权

暂停和恢复解决执行时序，却不能单独证明主体、工具、参数和资源获得合法授权。可靠审批必须绑定精确调用，并在工具内部保留最终鉴权。

### 13.4 Provenance、capability 和 IFC 更接近权限语义

CaMeL、Fides、PFI、MCP PEP 和 Tool Forge 不只检查内容，还追踪来源、标签和能力，因此比纯 scanner 更接近执行控制。但标签传播和 adapter 覆盖不完整时，保证仍会在边界处中断。

### 13.5 Scanner、validator 和 postcondition 只有支配 action sink 才是 enforcement

LlamaFirewall、Invariant、Guardrails、Agent Policy Guard、AgentDojo 和 HarnessAudit 都能产生有价值的信号；若信号被忽略、只影响评分或发生在副作用之后，它们属于检测或决策源，不是执行强制。

### 13.6 最强形态是分层组合

当前证据支持的目标结构是：

> specification/policy → provenance/capability → approval/authorization → unified gate → sandbox/OS interception → postcondition → constrained recovery → audit。

没有一个项目在当前证据中同时证明所有层、所有入口、所有异常和所有恢复路径均闭合。可以下结论说控制原语已经较丰富，但不能宣称开源生态普遍具备完整、E4 级 deployable harness 保证。

## 14. 局限与验收清单

本报告基于固定提交的静态代码审查、仓库内测试和少量本地运行，不是对 23 个对象统一安装、统一威胁模型和统一任务后的动态比较。部分项目是 notebook、prototype、SDK component 或策略源；部分提交受到 Windows 文件名、大小写碰撞、TLS 检出和依赖缺失影响。论文中的 ASR、utility、recall、conformance 或开销来自不同实验，不能横向合并。

后续若要把本报告升级为可发表的机制频数与效果研究，应完成以下验收：

- [x] RQ1 六类控制均有代码级机制描述。
- [x] 项目、生命周期、保证形式和组合结构四个分布轴分别回答。
- [x] 21 个 implementation unit 全部出现并具有稳定 ID。
- [x] AgentDojo、HarnessAudit 单列为 detector/postcondition。
- [x] 策略源、validator、scanner 未被误称为完整 harness。
- [x] 默认、异常、恢复和主要 bypass 已纳入分析。
- [x] multi-label、分母和去重规则已声明。
- [x] “未观察到”未被改写为“不存在”。
- [x] PPT 临时计数、混合 manifest、论文 E3 和 demo 未作强保证分母。
- [x] 本地测试按通过、失败、环境错误和未运行区分。
- [ ] 对 21 个实现建立统一、可重复执行的动态测试环境。
- [ ] 枚举每个项目全部副作用入口并验证 complete mediation。
- [ ] 对 no-match、parse、timeout、backend failure 和恢复路径做跨项目故障注入。
- [ ] 验证 approval 的主体、工具、参数、资源、session、expiry 和 revocation 绑定。
- [ ] 引入独立复现或生产证据，形成 E4 级结论。

## 15. 最终回答

RQ1 可以得到一份肯定但有限定的回答：当前纳入样本的开源 LLM Agent 项目已经在代码中实现了规范、约束、检测、恢复、授权和验证所需的大多数控制原语。它们分别落在 schema/contract、policy/IFC、approval/middleware、tool dispatcher、sandbox/OS hook、postcondition、recovery 和 audit 等层。21 个运行时或决策实现中，少数项目拥有较明确的执行或最终返回控制权，多数项目提供需要宿主接线的组件；另有两个检测/后置验收实现补足终态和轨迹证据。

这些控制的分布不是均匀的：规范和执行前 gate 最密集，副作用点控制、跨步状态、可信审批绑定、受约束恢复和不可丢失审计相对不足。保证形式也不是单一的，从 hard block、pause/approval、conditional continuation、soft feedback 到 post-hoc detection 和 isolation 并存。组合结构能否形成强保证，取决于 verdict 是否贯穿 policy、dispatcher、action sink、postcondition 和 recovery，并且所有旁路均受到同一控制。

因此，当前最准确的研究结论不是“某类 guardrail 已经解决指令遵从”，而是：开源项目已经实现了构建强 harness 所需的多个代码原语，但整体保证通常受最弱接线点、默认行为、异常分支和旁路限制；要从组件存在升级为 deployable harness 保证，仍需证明 complete mediation、精确授权、跨步状态、受约束恢复和完整审计。

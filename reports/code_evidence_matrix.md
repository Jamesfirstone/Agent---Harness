# 代码级证据矩阵

核验日期：2026-08-20。每条证据固定到本地仓库提交，提交清单见 [repo_manifest.md](../sources/repo_manifest.md)。证据等级采用：E0=仅文档/提示声称；E1=存在实现路径；E2=有针对性测试；E3=有对照、消融或行为测量；E4=独立复现或生产证据。本轮以静态审查和少量本地测试为主，未将 README 声称自动提升为代码证据。

| 项目 | 生命周期/机制 | 代码级证据 | 行为与边界 | 等级 |
|---|---|---|---|---|
| Microsoft Agent Governance Toolkit | 授权、策略、人工审批、审计 | `agent-governance-typescript/src/policy.ts:370,464,559`；`policy-engine/core/src/runtime.rs:160,337`；`policy-engine/core/src/verdict.rs:100,229`；`tests/e2e_python/scenarios/human_approval/test_human_approval.py:74-101` | 策略输出被正规化、验证并映射为 verdict；测试验证批准后恰好执行一次、拒绝时不执行。审计路径在 `agent-governance-typescript/src/audit.ts:14,58`。 | E2 |
| AgentDojo | 工具协议、注入检测、后置条件 | `src/agentdojo/functions_runtime.py:246-274`；`src/agentdojo/agent_pipeline/pi_detector.py:98-109`；`src/agentdojo/base_tasks.py`；`src/agentdojo/benchmark.py` | 未注册工具被拒绝，参数由 schema 验证；检测到注入时可抛出 `AbortAgentError`。任务成功/安全性由运行后状态检查，主要是 benchmark oracle，不是通用生产 gate。 | E2 |
| NVIDIA NeMo Guardrails | 输入、输出、工具调用、工具结果 rails | `nemoguardrails/guardrails/rails_manager.py:209,327,344,363,389,499,521`；`guardrails/actions/tool_call_action.py:38`；`tool_result_action.py:50`；`rail_guard.py:57-95` | 可串行或并行执行 rails，并校验 tool-call 与 tool-result 的名称/ID 链接。普通 rail 异常映射为不安全并阻断；上游 HTTP 状态异常会继续抛出，不能笼统写成“所有异常均 fail-closed”。 | E1–E2 |
| OpenAI Agents Python | 严格 schema、工具 guardrail、审批与恢复 | `src/agents/function_schema.py:23,473`；`src/agents/tool.py:441,480,483,486,595`；`src/agents/tool_guardrails.py:60`；`src/agents/run_internal/tool_execution.py:1300,2501`；`tests/mcp/test_mcp_approval.py:16-40` | 审批可暂停 run，批准后恢复且只执行一次；输入/输出 guardrail 可允许、拒绝或抛错。`src/agents/tool.py:419` 明示直接包装 callable 会绕过 schema、guardrail、timeout 和 tracing，是重要 bypass surface。 | E2 |
| Meta Purple Llama / LlamaFirewall | 扫描、代码安全、HITL | `LlamaFirewall/.../llamafirewall_data_types.py:22-24`；`llamafirewall.py:87,108,189`；`tests/test_replay_scan.py:30-70`；`scanners/regex_scanner.py:32,63`；`CodeShield/codeshield.py:37,48` | verdict 包含 `HITL`，replay scan 测试验证 decision/reason/score 传播；正则扫描器与 CodeShield 可产生 block/warn。扫描器只是决策源，是否阻断仍取决于调用方接线。 | E2 |
| τ-bench | 业务规则、工具调用协议、完成判定 | `tau_bench/envs/retail/rules.py:3-10`；`tau_bench/envs/base.py:90-164` | “先认证、变更前明确授权、一次一个工具”是给模型的规则文本，属于 specification，而非运行时 gate；环境在终止后比较数据库哈希和输出项，提供检测/奖励而非事前防止。 | E1 |
| τ²-bench | 多轮/多方交互与后置评估 | 本地仓库固定至 `a2c024725189`；作为 τ-bench 的后继基准保留完整实现 | 适合后续现代化复现；当前轮未逐路径审计，因此不把其 README 能力计入控制分布。 | E0–E1 |
| ActPlane | 执行隔离、授权、内核级副作用拦截 | `policies/readonly.yaml:7-12`；`test/policies/11_destructive_confirm.yaml:3-8`；`bpf/process.bpf.c:125-128,1766-1779,1866-1876,2229-2240` | eBPF/LSM 路径可对文件写、网络连接、强制删除等返回 `-EPERM` 或发送 `SIGKILL`；与提示规则不同，它在副作用发生点强制执行。依赖 Linux/eBPF 环境。 | E2–E3（论文测量） |
| Enterprise LLM Agent Harness | 结构验证、合同、恢复、消融 | `server/index.mjs:1029-1162`；`tests/guardrail-scorer.test.mjs`；`scripts/build-claim-promotion-review-packet.mjs` | prompt-only 分支记录失败但返回原输出；code-owned 分支在失败时进入确定性 composer fallback。论文/测试对比 prompt-only、外部 guardrail 与内置 harness，是“代码所有权决定能否阻断”的最直接证据之一。 | E3 |
| JSONSchemaBench | 结构验证与结构化输出评测 | `core/evaluator.py:18-54,57-128` | 使用 Draft 2020-12 验证 schema 与实例，并区分 declared/empirical coverage；JSON 解析与 schema 合规是可执行检查，但 benchmark 本身不是 agent runtime。 | E2 |
| IFEval | 严格/宽松指令判定 | `instruction_following_eval/evaluation_lib.py:75-157`；`instructions_registry.py` | strict 对每个 checker 求值并以 `all()` 聚合；loose 通过多种文本变体给出上界。它是可复现 evaluator，不是在线控制器。 | E2 |
| AGENTIF | 约束级评分与聚合 | `code4eval/1.evaluation_api.py:33-83,231-261` | CSR/ISR 在代码中聚合；checker 通过动态 `exec` 加载，未见隔离边界，直接运行不受信输入存在安全风险。属于评测证据，不是 agent action controller。 | E1–E2 |
| From Prompts to Templates artifact | 提示模板构成分析 | `code/component_identification.py:125` 及相邻重试/解析逻辑 | 提取并验证八类 prompt 组件，支持“规范层”的经验分析；未形成执行时强制控制。 | E1 |
| Testing-practices replication | 测试实践数据 | 仓库仅 6 个 tracked files，提交 `f850ad9e37c1` | 是研究复现材料，不是 harness。可用于抽样和分类，但不能当作运行时控制实现。 | E1 |
| Tangent artifact | 测试生成 | 本地仓库无提交、0 tracked files | 截至核验日公开 artifact 为空；论文结果可阅读，但本轮无法提取代码级或可复现证据。 | E0 |

## 综合判断

代码证据显示，最关键的划分不是“有没有规则文本”，而是规则是否位于不可绕过的执行路径。τ-bench 的业务规则主要属于模型可见的 specification；ActPlane 把规则落到内核副作用钩子；OpenAI Agents、NeMo 与 Governance Toolkit 位于工具调用/审批边界；JSONSchemaBench、IFEval 与 AgentIF 主要位于输出后的 evaluator。它们针对不同失效层，不能把同名的“guardrail”视为同等保证。

推荐把“具体 enforcement point”作为编码单元，并同时记录：生命周期位置、强制/检测/恢复类型、fail-open 或 fail-closed、状态是否持久化、允许粒度、bypass surface、测试等级以及组合顺序。这样才可解释一个项目为何有很多机制却仍然存在绕过路径。

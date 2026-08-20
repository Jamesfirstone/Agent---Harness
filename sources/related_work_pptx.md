# PPTX extraction: 相关工作.pptx

## Slide 1

- Agent指令遵循性相关工作调研
- 2026.08.18

## Slide 2

- AGENTIF: Benchmarking Instruction Following of Large Language Models in Agentic Scenarios

Notes:
- 当大语言模型作为 Agent 工作时，面对很长、约束很多、还涉及工具调用的复杂指令，它到底能不能真正“按要求办事”？
- 本文介绍了AgentIF，这是首个用于系统评估LLM在智能体场景中指令执行能力的基准测试。AgentIF具有三个关键特征：
- （1）真实性强，由50个现实世界的智能体应用构建而成。
- （2）篇幅长，平均每条指令包含1723个单词，最长可达15630个单词。
- （3）复杂性高，平均每条指令包含11.9个约束条件，涵盖多种约束类型，例如工具规范和条件约束。
- 为了构建AgentIF，我们从工业应用智能体和开源智能体系统中收集了50个智能体任务的707条人工标注指令。对于每条指令，我们都标注了相关的约束条件和相应的评估指标，包括基于代码的评估、基于LLM的评估以及混合代码-LLM评估。我们使用AgentIF系统地评估了现有的高级LLM。我们观察到，现有模型的性能普遍较差，尤其是在处理复杂的约束结构和工具规范方面。我们进一步对指令长度和元约束进行了误差分析和分析实验，并揭示了现有LLM的一些失效模式。
- 2. AGENTIF 怎么定义“复杂指令”？
- 论文把约束从两个维度进行分类。
- 第一维是约束类型：
- Formatting constraint：格式要求，例如 JSON、Markdown、表格、段落数量等。
- Semantic constraint：语义要求，例如内容完整性、关键词、深度、风格和语气。
- Tool constraint：工具使用要求，例如必须调用哪个工具、参数类型必须正确、禁止使用某些工具等。
- 其中 Tool constraint 是作者针对 Agent 场景重点引入的类型。
- 第二维是约束的呈现方式：
- Vanilla：直接明确告诉模型要求。
- Condition：只有某个条件满足时才需要执行。
- Example：并不明确写规则，而是让模型从示例中推断规则。
- 例如，“如果输出超过 100 个词，就加入关键词 paper”，就是典型的 conditional constraint。

## Slide 3

- AGENTIF: Benchmarking Instruction Following of Large Language Models in Agentic Scenarios

Notes:
- 怎么评价模型是否遵守了指令？
- AGENTIF 使用三种评测方式：
- Rule-based evaluation：适合关键词、格式等可以程序判断的规则。
- LLM-based evaluation：适合语气、完整性、语义等较主观要求。
- Hybrid evaluation：先让 LLM 提取相关内容，再用程序进行确定性检查。
- 论文主要采用两个指标：
- CSR（Constraint Success Rate）：单个约束满足率。
- ISR（Instruction Success Rate）：一整条指令中的所有约束都满足的比例。
- 论文测试了 GPT-4o、Claude 3.5 Sonnet、DeepSeek-R1、Qwen3-32B、o1-mini、Llama 3.1 等模型。
- 结果并不理想。
- 表现最好的模型在 CSR 上也只有约 60%；而更加严格的 ISR 指标最高只有 27.2%。也就是说，即使是较强模型，能够把一条复杂 Agent 指令中的所有要求全部满足的情况也不到三成。

## Slide 4

- AGENTIF: Benchmarking Instruction Following of Large Language Models in Agentic Scenarios
- 论文发现两个特别困难的类型：
- 第一，Conditional constraints。
- 模型不仅要“遵守规则”，还得先正确判断这个规则当前是否应该触发。作者对失败案例进一步分析，发现超过 30% 的部分错误来自条件判断本身，而不只是执行能力不足。
- 第二，Tool constraints。
- 工具使用主要存在四种错误：
- 使用了禁止的工具；
- 忘记调用必须使用的工具；
- 工具名称错误；
- 参数错误。
- 其中最常见的是不该用的工具却用了，或者应该调用的工具没有调用。论文还观察到一个有意思的现象：一些 reasoning / thinking 模型反而更容易忽略必须调用的工具，作者推测可能是因为它们更倾向于依赖自身知识。

Notes:
- 7. 指令越长，模型表现越差
- 论文第 8 页的 Figure 5 是一个很重要的结果：随着 instruction length 和 constraint count 增加，CSR 和 ISR 都明显下降。
- 尤其是当指令长度超过 6,000 词以后，几乎所有模型的 ISR 都接近 0。作者因此建议，现实 Agent 设计中不要无限增加 system prompt，而可以考虑把复杂任务拆分为几个子任务和更短的指令。
- 一个比较新颖的发现：Meta Constraints
- 论文还提出了 meta constraints（元约束）。
- 普通约束直接规定“回答应该怎样”，而元约束规定的是其他约束之间该怎样处理，例如：
- Constraint Selection：只执行若干规则中的某一个；
- Constraint Detailing：进一步细化某条规则；
- Constraint Prioritization：当规则冲突时，规定哪个优先。
- 大约 25% 的 AGENTIF 指令包含 meta constraints。论文发现，模型尤其不擅长 constraint selection，这说明模型在面对“规则管理规则”时仍然容易混乱。
- 这篇论文的核心结论
- 可以把全文压缩成一句话：
- 当前大语言模型虽然越来越会“解决问题”，但还远没有做到在复杂 Agent 场景中稳定、完整地遵守所有规则。

## Slide 5

- Instruction-Following Evaluation for Large Language Models(2023)
- 给模型一个包含明确约束的指令，然后检查模型是否严格满足这些约束。

Notes:
- 给模型一个包含明确约束的指令，然后检查模型是否严格满足这些约束。

## Slide 6

- JSONSchemaBench: A Rigorous Benchmark of Structured Outputs for Language Models

Notes:
- 2025 年的 JSONSchemaBench 已经收集约 10K 个真实 JSON Schema，并系统比较 Guidance、Outlines、llama.cpp、XGrammar、OpenAI、Gemini 等六类 constrained decoding / structured generation framework，评价 schema coverage、compliance、efficiency 和 output quality。可靠地生成结构化输出已成为现代语言模型 (LM) 应用的关键能力。约束解码已成为各领域在生成过程中强制执行结构化输出的主流技术。尽管其应用日益广泛，但对约束解码的行为和性能的系统性评估却鲜有开展。约束解码框架已围绕 JSON Schema 这种结构化数据格式进行标准化，大多数应用都保证在给定模式的情况下能够满足约束条件。然而，人们对这些方法在实践中的有效性仍然缺乏了解。
- 我们提出了一个评估框架，从三个关键维度评估约束解码方法：生成符合约束的输出的效率、对各种约束类型的覆盖范围以及生成输出的质量。为了便于评估，我们引入了 JSONSchemaBench，这是一个包含 1 万个真实世界 JSON 模式的约束解码基准测试，这些模式涵盖了各种复杂程度的约束。我们将基准测试与现有的官方 JSON Schema 测试套件相结合，并评估了六个最先进的约束解码框架，包括 Guidance、Outlines、Llamacpp、XGrammar、OpenAI 和 Gemini。

## Slide 7

- Empirical Study for Structured Output Control in LLMs for Software Engineering(2026)

Notes:
- 研究 LLM 生成结构化 output 时的可靠性，并比较：
- grammar-constrained decoding；
- regex validation；
- template-driven control。
- 结果说明 strict enforcement 能大量消除 syntax-level errors，但不能解决所有 structural / semantic errors。

## Slide 8

- Empirical Study for Structured Output Control in LLMs for Software Engineering

Notes:
- RQ1： 当前 LLM 在软件工程结构化输出中，语法错误和结构错误到底有多严重？
- RQ2： Grammar、Regex 等现有结构约束方法，能够在多大程度上改善输出有效性、正确性和稳定性？
- RQ3： 如果采用非常严格的模板约束，把“语法问题”尽可能排除以后，LLM 是否就能正确完成任务？

## Slide 9

- Empirical Study for Structured Output Control in LLMs for Software Engineering

## Slide 10

- Empirical Study for Structured Output Control in LLMs for Software Engineering

Notes:
- Syntax Error（语法错误）：输出无法解析，例如 JSON 少括号、代码编译失败。
- Structural Error（结构错误）：语法本身合法，但没有遵循指定 schema，例如缺少必填字段、函数调用签名不正确。
- Value Error（值/语义错误）：语法和结构都正确，但具体值或逻辑错误，例如函数参数填错、Python 程序能运行但结果错误。

## Slide 11

- From Prompts to Templates: A Systematic Prompt Template Analysis for Real-world LLMapps
- 从 GitHub 挖真实 LLM 软件，看开发者在 prompt 中采用了哪些 instruction practices，然后统计分布

Notes:
- 从 GitHub 挖真实 LLM 软件，看开发者在 prompt 中采用了哪些 instruction practices，然后统计分布

## Slide 12

- ActPlane: Programmable OS-Level Policy Enforcement  for Agent Harnesses
- 核心问题：自然语言里的 Agent instruction/policy，如何真正约束 Agent 最终在计算机系统里发生的行为？
- 核心结论：不能只相信 prompt，也不能只拦 tool call，而要把 policy 下沉到 OS kernel，在真正产生 side effect 的位置进行确定性 enforcement。

## Slide 13

- An Empirical Study of Testing Practices in Open Source AI Agent Frameworks and Agentic Applications
- 研究了：
- 39 个 open-source agent frameworks + 439 个 agentic applications
- 并识别出 10 种 testing patterns。研究还发现，传统 negative testing / membership testing 等大量存在，而类似 DeepEval 的 agent-specific testing 仅占约 1%；大量测试精力集中于确定性的 tool/workflow components，而 prompt/trigger 的测试非常少。

Notes:
- 研究了：
- 39 个 open-source agent frameworks + 439 个 agentic applications
- 并识别出 10 种 testing patterns。研究还发现，传统 negative testing / membership testing 等大量存在，而类似 DeepEval 的 agent-specific testing 仅占约 1%；大量测试精力集中于确定性的 tool/workflow components，而 prompt/trigger 的测试非常少。

## Slide 14

- Tangent: An Empirical Study of Testing Practices for LLM-Based Agent Applications
- 人工标注了：
- 2,572 个 test methods
- 来自 240 个 test modules
- 构造 23 种 testing patterns taxonomy
- 分析 fixture、data、objective、assertion、testing level
- 还访谈了 10 位 senior industry practitioners
- 并发现 Agent tests 普遍偏 unit-level、mocking 较多、validation 较浅，复杂 interaction 和 non-functional requirements 覆盖不足。

Notes:
- ASE2026
- 研究人工标注了：
- 2,572 个 test methods
- 来自 240 个 test modules
- 构造 23 种 testing patterns taxonomy
- 分析 fixture、data、objective、assertion、testing level
- 还访谈了 10 位 senior industry practitioners
- 并发现 Agent tests 普遍偏 unit-level、mocking 较多、validation 较浅，复杂 interaction 和 non-functional requirements 覆盖不足。

## Slide 15

- Measuring Agents in Production(2026.01)
- 访谈中的生产团队主要采用了几类做法：
- Read-only / 最小权限：有 6 个案例把 Agent 限制为只读。例如 SRE Agent 可以分析事故、生成 bug report、提出修复方案，但不能直接修改生产系统，最终执行动作交给工程师。
- Sandbox / simulated environment：有 3 个团队把 Agent 放在沙箱或模拟环境里，与真实生产系统隔离。论文给了一个很具体的代码迁移案例：Agent 先在一个 mirrored sandbox 中生成和测试代码变更，只有经过软件验证之后才允许 merge 到真实代码环境。也就是说，典型流程可以理解为：
- Agent proposal → Sandbox execution → compile/test/rule verification → pass → production 而不是：Agent → production 直接执行
- Wrapper API / abstraction layer：有团队不让 Agent 直接看到或调用底层生产工具，而是在 Agent 与 production environment 之间建立一层 wrapper API。Agent 只能调用经过限制的中间接口，底层函数和系统细节对 Agent 隐藏。
- Role-based access control：Agent 的权限与使用它的人的权限绑定，比如普通员工调用 Agent，就不能因为 Agent 本身而获得管理员能力。不过作者也特别指出，这一点目前仍然困难：如果工具和文档之间存在互相冲突的权限设置，Agent 仍可能绕过某些配置。
- Human approval / bounded autonomy：这可能比 sandbox 还普遍。论文发现 68% 的系统在人工介入前执行不到 10 步；高风险、面向外部用户的 Agent 尤其倾向于使用固定工作流、有限工具、限定检索源，并在关键动作前强制人工审批。

Notes:
- 论文通过 20 个深入访谈 case studies + 306 名 practitioner 的调查研究真实生产 Agent 是怎么构建和部署的。它的一个核心发现：
- 生产环境中的可靠性主要不是靠“模型本身变可靠”，而是靠 system-level design。
- 作者发现真实系统会使用：
- sandbox verification；
- rule-based checks；
- wrapper APIs；
- RBAC；
- fixed action sequences；
- limited tool access；
- human approval；
- workflow constraints；
- continuous correctness verification。
- 例如他们明确报告，生产系统会把有写权限的 Agent 放入 sandbox，通过 rule-based checks 后才允许进一步集成；还会用 wrapper API 限制 Agent 能看到和操作的生产系统，以及通过 RBAC 限制权限。
- “哪些集成进系统的方法让你相信 Agent 能持续产生高质量输出？”
- 选项包括：
- grammar / syntax checks；
- domain-specific rules；
- knowledge graph validation；
- citation verification；
- LLM-as-a-judge；
- cross-model validation；
- HITL 等。
- 在 deployed agents 中，74% 使用 human verification，52% 使用 model-based evaluation，42% 使用 rule-based methods。

## Slide 16

- From Prompts to Contracts: Harness Engineering for Auditable Enterprise LLM Agents(2026.07)
- 核心结论：
- 产品化以后，应当把确定性行为从 prompt 中迁移到 code、manifest、schema 和 validation artifacts 中。
- ablation 发现，在其研究的 enterprise agent 中，prompt-only 无法阻止某些 contract violations，而 code-owned enforcement 可以阻止。
- LLM 可以 propose，但 deterministic software 应当 verify / constrain / commit。

Notes:
- 论文提出：
- Prompt-dominant prototype
- ↓
- Contract-governed Agent
- 也就是把：
- “请模型遵守规则”
- 变成：
- “系统只允许满足规则的结果通过。”

## Slide 17

- From Prompts to Contracts: Harness Engineering for Auditable Enterprise LLM Agents(2026.07)
- 可靠智能体主要依靠系统级约束；本文则给出一种具体的系统级实现方式——Harness Engineering
- 原始文档
- ↓
- Source Manifest：登记来源、实体范围、状态和使用政策
- ↓
- Evidence Record：保存文件哈希、文本哈希和页码/行号
- ↓
- Claim Candidate：从资料中提取候选事实
- ↓
- Source-backed Claim：经准入后可在运行时使用的原子事实
- ↓
- 实体路由 → Claim选择 → 答案规划
- ↓
- LLM组合边界：模型只负责组织读者可见的语言
- ↓
- 输出契约验证
- ├─ 通过 → 返回答案
- └─ 失败 → 确定性模板回退
- ↓
- 读者答案 + 独立审计轨迹

Notes:
- 论文提出：
- Prompt-dominant prototype
- ↓
- Contract-governed Agent
- 也就是把：
- “请模型遵守规则”
- 变成：
- “系统只允许满足规则的结果通过。”
- 这里最关键的是“组合边界”：
- Harness决定什么可以说、根据什么证据说、回答属于哪个实体；
- LLM只负责把已经批准的材料组织成自然语言；
- LLM不能自行扩大数据来源或事实范围。

## Slide 18

- Agent Harness Engineering: A Survey（2026.05）
- 论文提出 ETCLOVG 七层分类，并建立了配套的开源项目目录。论文项目页｜OpenReview
- 它的中心论点是：
- 随着基础模型能力提高，生产智能体可靠性的约束因素逐渐从模型本身转向包围模型的执行基础设施，即Agent Harness。

Hyperlinks:
- [论文项目页](https://picrew.github.io/LLM-Harness/)
- [OpenReview](https://openreview.net/forum?id=eONq7FdiHa)

## Slide 19

- L0：生成提示
- 通过自然语言告诉模型需要什么：
- system prompt；
- 格式说明；
- few-shot examples；
- invalid/valid examples；
- chain-of-thought或planning要求；

## Slide 20

- 课题思路
- 定位：研究“开源 Agent 系统通过哪些代码级 Harness 控制保障指令执行，这些控制是否真的有效”。
- 标题：Beyond Prompts: An Empirical Study of Instruction-Compliance Controls in Open-Source LLM Agent Systems
- 研究对象：Agent Harness 中用于预防、检测、阻止或修复指令违反的、可观察的工程机制。

## Slide 21

- 具体研究对象
- Agent Harness 中用于预防、检测、阻止或修复指令违反的、可观察的工程机制。例如：
- 从 AGENTS.md、system prompt、配置文件加载和合并指令；
- 处理 system、developer、user、tool 等不同来源的优先级；
- JSON Schema、grammar、FSM、类型系统等结构化输出约束；
- 工具名称、参数、前置条件和调用顺序验证；
- 文件、网络、命令和工作目录权限控制；
- 状态机、工作流图、最大步数和终止条件；
- 解析失败后的重试、修复、回退和模型切换；
- 执行前审批、危险操作确认和人工介入；
- 测试、结果验证、轨迹记录和审计。
- 不纳入的对象：
- 仅存在于 prompt 中、没有系统实现的建议；
- 一般性能优化、RAG、memory 等与指令遵循无直接关系的功能

## Slide 22

- RQ1：开源 LLM Agent 系统在其 deployable harness 中实现了哪些用于规范、约束、检测、恢复、授权和验证指令执行的代码级控制？这些控制在项目、执行生命周期、保证形式与组合结构上的分布如何？

## Slide 23

- RQ1-机制列表
- 机制族 | Core实例 | 覆盖案例
- Structural validation | 10 | 5/5
- Output constraining | 7 | 4/5
- Postcondition/completion | 7 | 4/5
- Protocol/workflow | 6 | 4/5
- Recovery/resilience | 6 | 4/5
- Semantic/context validation | 5 | 4/5
- Specification | 5 | 4/5
- Authorization/capability | 4 | 2/5

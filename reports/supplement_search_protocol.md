# 补充性系统映射研究协议：Agent Harness 的指令遵从实现

**协议冻结时间：2026-08-20（Asia/Shanghai）**  
**综述类型：**补充性系统映射研究（systematic mapping study），报告参照 PRISMA-ScR；本协议在正式检索前建立。  
**基线排除集：**《相关工作.pptx》及 `sources/paper_index.md` 已列 11 篇论文/资料和 `sources/repo_manifest.md` 已列 16 个仓库。

## 1. 研究问题

- **RQ1：**现有 PPT 之外，哪些论文或开源实践在 agent harness 中实现了可执行的指令遵从控制？
- **RQ2：**这些控制位于规范、模型输出、工具调用、授权审批、执行隔离、状态转换、后置条件、恢复和审计中的哪个位置？
- **RQ3：**代码所有者、失败语义、状态持久性和 bypass surface 如何影响保证强度？
- **RQ4：**哪些控制具有实现、针对性测试、行为测量、消融或生产证据，哪些只停留在文档或 prompt 声称？

## 2. 概念与检索词

| 概念组 | 主要同义词 |
|---|---|
| Agent 系统 | `LLM agent`, `language model agent`, `agentic system`, `AI agent`, `tool-using agent` |
| Harness/控制层 | `agent harness`, `guardrail`, `middleware`, `control plane`, `policy enforcement`, `runtime monitor`, `contract`, `governance` |
| 指令遵从 | `instruction following`, `instruction compliance`, `constraint`, `policy compliance`, `rule following`, `invariant` |
| 执行机制 | `tool call validation`, `function calling`, `authorization`, `approval`, `permission`, `sandbox`, `postcondition`, `rollback`, `recovery`, `audit` |

预注册查询族：

1. `("LLM agent" OR "language model agent") AND (harness OR guardrail OR middleware OR "policy enforcement") AND ("instruction following" OR compliance OR constraint)`
2. `(agentic OR "AI agent") AND ("tool call" OR "function calling") AND (validation OR approval OR permission OR authorization OR sandbox)`
3. `("LLM agent" OR "AI agent") AND (runtime OR execution) AND (monitor OR contract OR policy OR guardrail)`
4. `("agent workflow" OR "agentic workflow") AND (postcondition OR invariant OR rollback OR recovery OR audit)`
5. 针对纳入种子的题名、作者、引用和 references 做前向/后向雪球追踪。

## 3. 数据源与执行顺序

1. Parallel Web academic-focused search：限定 arXiv、ACM、IEEE、OpenReview、Springer、Semantic Scholar 等学术域。
2. Parallel Web general search：补充 GitHub、官方文档、项目页与技术实践。
3. arXiv API：覆盖计算机科学预印本并保存原始 Atom/XML 或转换后的 JSON。
4. OpenAlex：跨学科题名/摘要检索、引用数与引用网络。
5. Semantic Scholar：题名匹配、相关推荐、前向/后向引用；若共享限流失败则记录并用 OpenAlex 替代。
6. Crossref：核验 DOI、正式 venue、作者和发表状态。
7. GitHub/官方仓库：核验代码、license、commit、测试与 release；博客仅用于发现，不作为论文结论证据。

每次检索记录：数据源、完整查询、时间、结果总数、导出文件、错误/限流和替代路径。原始结果保存在 `sources/supplement/search_raw/`，筛选表保存在 `sources/supplement/`。

## 4. 纳入标准

候选必须同时满足：

1. 题名/摘要/全文或官方文档明确涉及 LLM/AI agent 的运行时、harness、中间件或执行治理；
2. 至少实现一种可执行控制：结构验证、工具/参数验证、能力授权、人工审批、工作流状态约束、运行时隔离、后置条件、恢复或审计；
3. 能取得论文全文、正式 artifact，或可公开检查的开源仓库；
4. 不在既有 PPT 论文清单和当前仓库清单中；
5. 英文或中文，2019-01-01 至 2026-08-20；重要的早期基础工作可经理由说明后纳入。

## 5. 排除标准

- 纯模型 alignment / RLHF / instruction tuning，没有 harness 执行机制；
- 纯 instruction-following benchmark，且没有 runtime control；
- 纯 prompt engineering 或仅给 system prompt 建议；
- 只描述 prompt injection 攻击而不实现防护执行路径；
- 纯结构化输出、observability、评测或不确定性估计，未支配动作、状态或恢复；
- 闭源产品宣传、无法核验代码/全文、重复版本、撤稿或与 agent 无直接关系；
- 已被《相关工作.pptx》或当前本地证据集覆盖。

## 6. 筛选与去重

按 DOI、arXiv ID、规范化题名依次去重。流程为：检索命中 → 去重 → 题名/摘要筛选 → 全文/artifact 筛选 → 纳入论文 → 可分析仓库。每个排除项保留一个主要理由；预印本和正式版本合并为一条，以正式版本为主并保留版本关系。

## 7. 数据提取与质量评价

每篇论文提取题名、作者、年份、venue/状态、DOI/arXiv、全文、代码、研究设计、样本/任务、机制、关键结果、作者局限与本轮局限。每个仓库固定 upstream 和 commit，并记录语言、license、入口、具体文件/符号/测试、控制对象、生命周期位置、fail-open/closed、状态性、bypass surface 和本地验证结果。

证据等级沿用主报告：E0=文档/prompt 声称；E1=实现路径；E2=针对性测试；E3=行为测量/消融；E4=独立复现或生产证据。论文质量另按元数据可信度、设计透明度、artifact 可用性和结论-证据匹配度评为 High/Moderate/Low，避免用引用数替代方法质量。

## 8. 偏倚控制与变更规则

- 搜索至少覆盖三类学术数据库和一类工程来源；同一结论优先引用论文与代码主来源。
- 将预印本、同行评审论文、技术报告和工程实践分层，不混写发表状态。
- 正向结果和失败/空 artifact/缺测试同样记录。
- 查询式允许基于试检索增加同义词，但不得删除原查询；任何修改写入检索日志并给出理由。
- 本轮为单主审查者加独立 worker 的快速系统映射，不声称达到注册系统综述或双盲筛选标准；分歧由回到全文和调用路径解决。

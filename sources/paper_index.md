# 论文与资料索引（核验日期：2026-08-20）

本索引把《相关工作.pptx》中涉及的论文与本地下载件一一对应。`论文状态`按截至核验日期能够确认的官方页面填写；arXiv 预印本不写成已正式发表。PDF 的页数、字节数与 SHA-256 见 [paper_manifest.md](paper_manifest.md)。

| 主题 | 论文/资料 | 年份与状态 | 本地 PDF | 官方标识或项目 | 对 PPT 的关键校正 |
|---|---|---|---|---|---|
| 指令遵循 | AGENTIF: Benchmarking Instruction Following of Large Language Models in Agentic Scenarios | NeurIPS 2025 Datasets & Benchmarks | [PDF](../papers/agentif_2025.pdf) | [arXiv:2505.16944](https://arxiv.org/abs/2505.16944)；[代码](https://github.com/THU-KEG/AgentIF) | 50 个应用、707 条指令、平均 11.9 个约束得到支持；正文同时出现“1723 words”和结论“1717 tokens”，单位不应混用。 |
| 指令遵循 | Instruction-Following Evaluation for Large Language Models (IFEval) | 2023 arXiv 预印本 | [PDF](../papers/ifeval_2023.pdf) | [arXiv:2311.07911](https://arxiv.org/abs/2311.07911)；[代码](https://github.com/google-research/google-research/tree/master/instruction_following_eval) | 基准通常概括为约 500 个提示；发行实例为 541，含 25 类可验证指令。 |
| 结构化输出 | JSONSchemaBench: A Rigorous Benchmark of Structured Outputs for Language Models | ICML 2025 ES-FoMo III Workshop | [PDF](../papers/jsonschemabench_2025.pdf) | [arXiv:2501.10868](https://arxiv.org/abs/2501.10868)；[代码](https://github.com/epfl-dlab/jsonschemabench) | 精确规模为 9,558 个 schema；核心维度是效率、覆盖率和质量，compliance 属于覆盖率分析。 |
| 结构化输出 | An Empirical Study for Structured Output Control in LLMs for Software Engineering | 2026 arXiv 预印本 | [PDF](../papers/structured_output_control_se_2026.pdf) | [arXiv:2606.09395](https://arxiv.org/abs/2606.09395)；[数据](https://figshare.com/s/7d63a114a63fdf081067) | PPT 将 RQ2/RQ3 对调；语法抑制不能消除结构错误与值错误。未确认公开 GitHub 仓库。 |
| 提示工程 | From Prompts to Templates: A Systematic Prompt Template Analysis for Real-world LLMapps | FSE Companion 2025 Industry Track | [PDF](../papers/prompts_to_templates_2025.pdf) | [DOI:10.1145/3696630.3728533](https://doi.org/10.1145/3696630.3728533)；[代码](https://github.com/RedSmallPanda/FSE2025) | 样本来自经筛选的 GitHub 开源 LLM 应用/PromptSet，不代表全部真实生产应用。 |
| 系统级执行控制 | ActPlane: A Control Plane for Agentic Systems | 2026 arXiv 预印本 | [PDF](../papers/actplane_2026.pdf) | [arXiv:2606.25189](https://arxiv.org/abs/2606.25189)；[代码](https://github.com/eunomia-bpf/ActPlane) | 是 Linux/eBPF 原型，约束对象是内核钩子、权限和副作用；报告开销 1.9%–8.4%，不能泛化为所有 agent harness。 |
| 测试实践 | Testing Practices in Open-Source AI Agent Frameworks and Applications | Empirical Software Engineering 31(124), 2026 | [PDF](../papers/testing_practices_oss_agents_2026.pdf) | [DOI:10.1007/s10664-026-10857-9](https://doi.org/10.1007/s10664-026-10857-9)；[复现包](https://github.com/SAILResearch/replication-25-agent-testing-empirical-study) | 39 个框架、439 个应用；手工分析 759 个测试函数。约 1% 指的是特定 agent 测试（如非确定性/DeepEval），不是全部测试。 |
| 测试生成 | Tangent: Targeted Agentic Test Generation for Python | ASE 2026 accepted/forthcoming | [PDF](../papers/tangent_ase2026.pdf) | [DOI:10.1145/3832783.3837414](https://doi.org/10.1145/3832783.3837414)；[Artifact](https://github.com/aster-test-generation/tangent-ase-2026) | 论文报告 2,572 个方法、240 个模块、23 个模式和 10 次访谈；截至核验日 artifact 仓库为空，暂不能据此复现。 |
| 生产评测 | Measuring Agents in Production | ICML 2026 Oral（arXiv v4 标注） | [PDF](../papers/measuring_agents_in_production_2026.pdf) | [arXiv:2512.04123](https://arxiv.org/abs/2512.04123) | 分析样本是 20 个访谈/案例与 86 个已部署或试点系统；306 是未筛选受访者，不能当成最终样本量。 |
| 合同化 harness | From Prompts to Contracts: Engineering Enterprise-Grade LLM Agent Harnesses | 2026 arXiv 预印本 | [PDF](../papers/prompts_to_contracts_2026.pdf) | [arXiv:2607.08028](https://arxiv.org/abs/2607.08028)；[代码](https://github.com/hammerbaki/enterprise-llm-agent-harness) | 证据来自韩国 5 个集团、25 家上市公司这一限定案例；270 次组合实验中 code-owned harness 为 120/120，外部 guardrail 为 88/120。 |
| 综述/目录 | Agent Harness Engineering: A Survey | TMLR 投稿 under review | [PDF](../papers/agent_harness_engineering_survey_2026.pdf) | [OpenReview](https://openreview.net/forum?id=eONq7FdiHa)；[项目](https://picrew.github.io/LLM-Harness/)；[目录](https://github.com/Picrew/awesome-agent-harness) | ETCLOVG 是 Execution、Tooling、Context、Lifecycle、Observability、Verification、Governance。摘要“170+”与当前网页分类计数来自不同快照，不能混用分母。 |

## 本地完整性

11 份 PDF 均通过 `%PDF` 头、页数读取、文本抽取和 SHA-256 检查。抽取文本位于 `papers/text/`，便于全文检索；本索引不把预印本状态、美化后的整数或不同数据快照混写为同一种证据。

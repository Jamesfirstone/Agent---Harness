# Agent Harness related-work evidence package

本仓库保存《相关工作.pptx》对应的文献核验、论文原文、代码级证据与固定版本的开源仓库。

## 主要交付物

- `reports/agent_harness_related_work_report.pdf`：综合报告 PDF。
- `reports/agent_harness_related_work_report.md`：可检索、可继续编辑的报告源文件。
- `reports/code_evidence_matrix.md`：固定到文件与行号的代码证据矩阵。
- `sources/paper_index.md`：论文元数据、官方入口与 PPT 校正。
- `sources/paper_manifest.*`：本地 PDF 页数、大小和 SHA-256。
- `sources/repo_manifest.*`：仓库 upstream、commit、分支与状态。
- `figures/harness_control_chain.png`：控制生命周期概念图。

### PPT 之外的补充系统映射（2026-08-20）

- `reports/supplement_harness_instruction_compliance_review.pdf`：论文、工程实践与代码证据综合报告。
- `reports/supplement_harness_instruction_compliance_review.md`：报告源文件。
- `reports/supplement_search_protocol.md`：检索前冻结的研究问题、查询族、纳排标准与偏倚控制。
- `sources/supplement/`：原始查询、650 条记录、去重候选、113 条详细筛选决定、下载/clone 清单与本地测试结果。
- `papers/supplement/`：16 篇新增论文 PDF 及 SHA-256/页数清单。
- `repos/supplement/`：18 个新增论文实现和工程实践的固定 commit。
- `figures/supplement/`：PRISMA 风格筛选图与完整调解机制图。

## 第三方仓库

可正常固定提交的第三方仓库以 Git submodule 保存。克隆时使用：

```bash
git clone --recurse-submodules git@github.com:Jamesfirstone/Agent---Harness.git
```

`tangent-ase2026` 截至 2026-08-20 仍是无提交的空 artifact，不能创建 gitlink。Google Research 仓库含 Windows 非法文件名，本地 IFEval 使用稀疏/归档物化；可移植源码保存在 `sources/ifeval-source.zip`，精确上游提交见 `sources/repo_manifest.md`。

补充仓库中 TrustAgent 含 Windows 不允许的冒号文件名；PydanticAI 的 partial clone 在 TLS 中断后缺少工作树对象；ToolSafe 同时跟踪 `README.md`/`readme.md`，在 Windows 大小写不敏感文件系统发生碰撞。三者的 Git HEAD 仍固定在 `repos/supplement/manifest.json`，但本地工作树被明确标为 partial，不应声称可直接运行。

## 可复现性边界

本仓库不保存浏览器 profile、PDF 渲染缓存、PPT 页图、全文文本抽取件和一次性解析脚本。这些内容可由原始 PDF/PPT 抽取重建，并不属于研究交付物。测试通过、缺依赖和失败结果统一记录在 `reports/test_results.md`。

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

## 第三方仓库

可正常固定提交的第三方仓库以 Git submodule 保存。克隆时使用：

```bash
git clone --recurse-submodules git@github.com:Jamesfirstone/Agent---Harness.git
```

`tangent-ase2026` 截至 2026-08-20 仍是无提交的空 artifact，不能创建 gitlink。Google Research 仓库含 Windows 非法文件名，本地 IFEval 使用稀疏/归档物化；可移植源码保存在 `sources/ifeval-source.zip`，精确上游提交见 `sources/repo_manifest.md`。

## 可复现性边界

本仓库不保存浏览器 profile、PDF 渲染缓存、PPT 页图、全文文本抽取件和一次性解析脚本。这些内容可由原始 PDF/PPT 抽取重建，并不属于研究交付物。测试通过、缺依赖和失败结果统一记录在 `reports/test_results.md`。

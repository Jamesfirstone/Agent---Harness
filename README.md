# Agent Harness related-work evidence package

本仓库保存《相关工作.pptx》对应的文献核验、论文原文、代码级证据与固定版本的开源仓库。

## 报告导航（按创建顺序编号）

`reports/` 的正式交付物已按首次进入 Git 的时间排序；同一提交内使用原始创建时间辅助排序。完整映射、内容说明和编号依据见 [`00_报告目录与编号说明.md`](reports/00_报告目录与编号说明.md)。

当前最终交付物是：

- `reports/08_最终Agent指令不遵从定义与Harness代码级审查.md`：论文定义、证据边界和代码级实现的可检索源文档。
- `reports/09_最终Agent指令不遵从定义与Harness代码级审查.pdf`：上述最终报告的排版版本。
- `figures/final/enforcement_guarantee_ladder.svg`：从规则存在到完整调解、闭合控制链的保证等级图。

基础证据入口保持在 `sources/paper_index.*`、`sources/paper_manifest.*`、`sources/repo_manifest.*`、`sources/supplement/`、`papers/`、`papers/supplement/`、`repos/` 与 `repos/supplement/`。

## 第三方仓库

可正常固定提交的第三方仓库以 Git submodule 保存。克隆时使用：

```bash
git clone --recurse-submodules git@github.com:Jamesfirstone/Agent---Harness.git
```

`tangent-ase2026` 截至 2026-08-20 仍是无提交的空 artifact，不能创建 gitlink。Google Research 仓库含 Windows 非法文件名，本地 IFEval 使用稀疏/归档物化；可移植源码保存在 `sources/ifeval-source.zip`，精确上游提交见 `sources/repo_manifest.md`。

补充仓库中 TrustAgent 含 Windows 不允许的冒号文件名；PydanticAI 的 partial clone 在 TLS 中断后缺少工作树对象；ToolSafe 同时跟踪 `README.md`/`readme.md`，在 Windows 大小写不敏感文件系统发生碰撞。三者的 Git HEAD 仍固定在 `repos/supplement/manifest.json`，但本地工作树被明确标为 partial，不应声称可直接运行。

## 可复现性边界

本仓库不保存浏览器 profile、PDF 渲染缓存、PPT 页图、全文文本抽取件和一次性解析脚本。这些内容可由原始 PDF/PPT 抽取重建，并不属于研究交付物。测试通过、缺依赖和失败结果统一记录在 `reports/02_本地验证记录.md`。

# 本地验证记录

执行日期：2026-08-20。未安装第三方依赖，未修改克隆仓库代码。

| 对象 | 命令/检查 | 结果 | 解释 |
|---|---|---|---|
| 11 份论文 PDF | 文件头、页数、文本抽取、SHA-256 | 11/11 可读 | 明细见 `sources/paper_manifest.md`。 |
| Enterprise harness 核心 guardrail | `node --test tests/detectors.test.mjs tests/guardrail.test.mjs tests/guardrail-scorer.test.mjs` | 23 passed, 0 failed | 支持检测、guardrail 与 scorer 的确定性路径。 |
| Enterprise harness 全量测试 | `node --test tests/*.test.mjs` | 34 total；25 passed；9 failed | 2 个 collector/ablation 断言差异；7 个 harness endpoint 返回 HTTP 500。说明本地快照并非全量绿，不应只报告核心子集。 |
| IFEval | Python unittest 导入 | 未进入测试，缺少 `absl` | 属于环境依赖缺失，不等于测试失败；本轮未安装依赖。 |
| JSONSchemaBench | Python smoke import | 导入失败，缺少 `dacite` | 同上；静态实现路径已核验，未声称完成运行时复现。 |
| PPT | OOXML 文本/备注/链接抽取；23 页 PNG 导出 | 23/23 成功 | 抽取件见 `sources/related_work_pptx.*`，页图见 `sources/pptx_slides/`。 |
| 仓库 | Git origin、commit、tracked files、clean 状态 | 16 个仓库已登记 | IFEval 因 Windows 非法文件名采用稀疏/归档物化，工作树显示非 clean；Tangent artifact 为空仓库。 |

这份记录刻意区分“静态代码证据”“测试通过”“环境未满足”和“全量测试失败”。前者不能自动替代后者，局部通过也不能代表仓库整体可复现。

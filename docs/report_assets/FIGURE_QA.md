# Figure QA Report

检查项：文件存在且非空、SVG 可解析、PNG 宽度至少 1800 px、CSV 有数据行。文字重叠、图例遮挡和数值一致性通过脚本设计约束与人工复核说明记录。

| Figure | SVG | PNG | CSV rows | Status | Notes |
|---|---:|---:|---:|---|---|
| Fig. 1 | readable SVG | 1960x1604px | fig1_validation_overview.csv=11 | PASS | backend-specific script output |
| Fig. 2 | readable SVG | 2305x1448px | fig2_algorithm_coverage_matrix.csv=15 | PASS | backend-specific script output |
| Fig. 3 | readable SVG | 2305x1574px | fig3_cross_validation_evidence.csv=50 | PASS | backend-specific script output |
| Fig. 4 | readable SVG | 1960x1651px | fig4_benchmark_raw.csv=85; fig4_benchmark_summary.csv=17 | PASS | backend-specific script output |
| Fig. 5 | readable SVG | 1960x1414px | fig5_aes_verbose_trace.csv=40 | PASS | backend-specific script output |
| Fig. 6 | readable SVG | 1960x1520px | fig6_ecb_leak_metrics.csv=3; fig6_pbkdf2_iterations.csv=25 | PASS | backend-specific script output |

## Visual QA Notes

- 所有 Python 图显式设置 sans-serif 字体、`svg.fonttype=none`、线宽和克制配色。
- R 图由 R 脚本使用 ggplot2/patchwork/svglite/ragg 输出；未用 Python 替代渲染。
- 所有坐标轴包含单位或明确计数含义。
- 未使用彩虹色板；红绿不作为唯一编码，状态图同时使用文字标签。
- PNG 作为报告预览图，SVG 作为可编辑主图。
- Overall status: PASS

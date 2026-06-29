# CryptoLab Report Figure Index

生成时间：待脚本运行后由 `scripts/figures/check_figures.py` 复核。

本索引采用 `nature-figure` 工作流的 figure contract：先声明结论、证据链、图型选择、导出格式和审稿风险，再通过 Python 或 R 脚本生成图像。所有图均为实验数据图，不包含架构图、流程图、ER 图或调用链图。

## Figure 1

- `figure_id`: Fig. 1
- 中文标题：测试验证总览图
- English short title: Validation overview
- Backend: Python / matplotlib
- Core conclusion: CryptoLab 的 Rust、API、前端构建和 Docker 配置验证形成了可追溯的工程验收基线，但 Docker 构建仍受本机 daemon 状态限制。
- Figure archetype: quantitative grid
- Target journal/output: Nature-style double-column report figure, SVG + PNG
- Final size: 183 mm × 120 mm
- Panel map:
  - A: Rust / API / Frontend / Docker 验证状态 tile chart
  - B: Rust cargo test passed / failed / ignored stacked bar
  - C: API pytest passed / failed / deselected stacked bar
  - D: 前端 npm test 与 npm run build 状态对比
- Evidence hierarchy:
  - Hero evidence: Panel A 汇总全部验证层状态
  - Validation evidence: Panels B-C 给出真实测试计数
  - Controls/robustness: Panel D 诚实显示测试脚本与构建结果差异
- Statistics needed: 测试数量为一次本机命令输出计数，无误差条
- Source data needed: `docs/PROGRESS.md`, `docs/progress_evidence/20_cargo_test_tail.txt`, `21_pytest_tail.txt`, `22_frontend_npm_test_tail.txt`, `23_frontend_build_tail.txt`, `24_docker_build_tail.txt`
- Image-integrity notes: 纯矢量统计图；PNG 为脚本导出预览
- Reviewer risk: Docker build 失败原因是 daemon 不可用，不应表述为镜像构建通过
- Data source: 实际命令输出归档
- Script: `scripts/figures/plot_validation_overview.py`
- Outputs:
  - `docs/report_assets/figures/fig1_validation_overview.svg`
  - `docs/report_assets/figures/fig1_validation_overview.png`
  - `docs/report_assets/data/fig1_validation_overview.csv`
- Reproducible command: `.\.venv\Scripts\python.exe scripts\figures\plot_validation_overview.py`

## Figure 2

- `figure_id`: Fig. 2
- 中文标题：算法覆盖与实现状态矩阵
- English short title: Algorithm coverage matrix
- Backend: R / ggplot2 + patchwork
- Core conclusion: 课程要求的 15 个算法均有实现与测试证据，唯一算法层限制是 RC6 的模式覆盖为 ECB/CBC。
- Figure archetype: quantitative grid
- Target journal/output: Nature-style double-column report figure, SVG + PNG
- Final size: 183 mm × 115 mm
- Panel map:
  - A: 按编码、哈希、对称、公钥分类的实现状态矩阵
  - B: 测试向量来源边注矩阵
- Evidence hierarchy:
  - Hero evidence: Panel A 展示 15/15 覆盖和 RC6 partial 标记
  - Validation evidence: Panel B 连接 RFC/NIST/GB/T/cryptography/hashlib/gmssl 等来源
  - Controls/robustness: Docker/前端脚本风险不混入算法层
- Statistics needed: 算法覆盖计数，无误差条
- Source data needed: `docs/PROGRESS.md`, `docs/cross_validation_matrix.md`, `rust_core/src/**`, `api_server/tests/test_cross_validation.py`
- Image-integrity notes: 纯矢量 tile matrix
- Reviewer risk: RC6 不应被渲染成 full-mode implemented；ECDSA secp160r1 第三方库不可用属于验证限制而非缺实现
- Data source: 项目进度报告、交叉验证矩阵、源码文件存在性和测试文件证据
- Script: `scripts/figures/plot_algorithm_coverage_matrix.R`
- Outputs:
  - `docs/report_assets/figures/fig2_algorithm_coverage_matrix.svg`
  - `docs/report_assets/figures/fig2_algorithm_coverage_matrix.png`
  - `docs/report_assets/data/fig2_algorithm_coverage_matrix.csv`
- Reproducible command: `Rscript scripts/figures/plot_algorithm_coverage_matrix.R`
- Execution status: 已执行；使用 `D:\Development\R-4.6.0\bin\x64\Rscript.exe` 与 `ggplot2 + patchwork + svglite/ragg` 原始 R 设计生成。
- Refined paper-style outputs:
  - `docs/report_assets/figures/fig2_algorithm_coverage_refined.pdf`
  - `docs/report_assets/figures/fig2_algorithm_coverage_refined.png`
  - `docs/report_assets/data/fig2_algorithm_coverage_refined.csv`
- Refined script: `scripts/figures/plot_algorithm_coverage_refined.R`
- Refined reproducible command: `D:\Development\R-4.6.0\bin\x64\Rscript.exe scripts/figures/plot_algorithm_coverage_refined.R`

## Figure 3

- `figure_id`: Fig. 3
- 中文标题：交叉验证证据矩阵
- English short title: Cross-validation evidence
- Backend: R / ggplot2 + patchwork
- Core conclusion: 关键算法不只通过单元测试，还被 KAT、第三方库对照、HTTP API、前端构建和 verbose/demo 支持等多层证据覆盖。
- Figure archetype: quantitative grid
- Target journal/output: Nature-style double-column report figure, SVG + PNG
- Final size: 183 mm × 125 mm
- Panel map:
  - A: 算法 × 证据层 tile matrix
  - B: 每类证据通过/部分/无证据的计数摘要
- Evidence hierarchy:
  - Hero evidence: Panel A 显示每个算法族的证据完整性
  - Validation evidence: Panel B 统计证据层覆盖
  - Controls/robustness: RC6/ECDSA 的第三方库缺口明确标为 partial/no evidence
- Statistics needed: 证据单元格计数，无误差条
- Source data needed: `docs/cross_validation_matrix.md`, `docs/PROGRESS.md`, `api_server/tests/*.py`, `rust_core/src/**/tests`
- Image-integrity notes: 纯矢量 evidence matrix
- Reviewer risk: 前端构建只能证明集成构建链路，不等同于逐算法端到端 UI 测试
- Data source: 交叉验证矩阵、测试文件、进度报告
- Script: `scripts/figures/plot_cross_validation_evidence.R`
- Outputs:
  - `docs/report_assets/figures/fig3_cross_validation_evidence.svg`
  - `docs/report_assets/figures/fig3_cross_validation_evidence.png`
  - `docs/report_assets/data/fig3_cross_validation_evidence.csv`
- Reproducible command: `Rscript scripts/figures/plot_cross_validation_evidence.R`
- Execution status: 已执行；使用 `D:\Development\R-4.6.0\bin\x64\Rscript.exe` 与 `ggplot2 + patchwork + svglite/ragg` 原始 R 设计生成。
- Refined paper-style outputs:
  - `docs/report_assets/figures/fig3_cross_validation_refined.pdf`
  - `docs/report_assets/figures/fig3_cross_validation_refined.png`
  - `docs/report_assets/data/fig3_cross_validation_refined.csv`
  - `docs/report_assets/data/fig3_cross_validation_refined_counts.csv`
- Refined script: `scripts/figures/plot_cross_validation_refined.R`
- Refined reproducible command: `D:\Development\R-4.6.0\bin\x64\Rscript.exe scripts/figures/plot_cross_validation_refined.R`

## Figure 4

- `figure_id`: Fig. 4
- 中文标题：Benchmark 性能结果图
- English short title: Benchmark performance
- Backend: Python / matplotlib
- Core conclusion: 实测 benchmark 显示吞吐型算法、KDF/HMAC 和公钥操作处在不同数量级，报告应分面比较而不是用单一坐标轴混排。
- Figure archetype: quantitative grid
- Target journal/output: Nature-style double-column report figure, SVG + PNG
- Final size: 183 mm × 130 mm
- Panel map:
  - A: 对称加密吞吐量 MB/s，bar + jitter points
  - B: 哈希吞吐量 MB/s，bar + jitter points
  - C: RSA/ECDSA 公钥操作 ms/op，log-scale dot plot
  - D: HMAC/PBKDF2 ms/op 对比，bar + jitter points
- Evidence hierarchy:
  - Hero evidence: Panels A-B 显示吞吐型算法主结果
  - Validation evidence: Panels C-D 展示低吞吐操作的耗时量级
  - Controls/robustness: 每算法至少 5 次重复并输出 raw + summary CSV
- Statistics needed: mean, median, min, max, n；bar 表示 mean，点表示重复测量
- Source data needed: `api_server/app/services/benchmark_service.py` 或 `cryptolab_core` 真实调用
- Image-integrity notes: 纯矢量统计图；不使用随机伪造数据，jitter 仅为显示重复点的位置偏移
- Reviewer risk: benchmark 是单机短时测量，受本机负载影响；脚本保留 raw 数据和测量时间戳
- Data source: 真实 benchmark 脚本运行输出
- Scripts:
  - `scripts/figures/run_benchmarks.py`
  - `scripts/figures/plot_benchmark_performance.py`
- Outputs:
  - `docs/report_assets/figures/fig4_benchmark_performance.svg`
  - `docs/report_assets/figures/fig4_benchmark_performance.png`
  - `docs/report_assets/data/fig4_benchmark_raw.csv`
  - `docs/report_assets/data/fig4_benchmark_summary.csv`
- Reproducible commands:
  - `.\.venv\Scripts\python.exe scripts\figures\run_benchmarks.py`
  - `.\.venv\Scripts\python.exe scripts\figures\plot_benchmark_performance.py`

## Figure 5

- `figure_id`: Fig. 5
- 中文标题：AES verbose trace 结果图
- English short title: AES verbose trace
- Backend: Python / matplotlib
- Core conclusion: AES verbose mode 提供 FIPS 197 可对照的真实 round-level state trace，而不是仅给出最终 ciphertext。
- Figure archetype: quantitative grid
- Target journal/output: Nature-style double-column report figure, SVG + PNG
- Final size: 183 mm × 130 mm
- Panel map:
  - A: 10 rounds × 4 intermediate states 的 byte-change heatmap
  - B: Round 0/5/10 state matrix 小面板
  - C: 每轮 timing ns bar chart
  - D: FIPS 197 对照通过状态
- Evidence hierarchy:
  - Hero evidence: Panel A 显示中间状态逐轮可见
  - Validation evidence: Panel B 展示关键轮 state matrix
  - Controls/robustness: Panel D 与测试文件锁定 FIPS 197 向量
- Statistics needed: timing 为一次 trace 内记录，非重复 benchmark
- Source data needed: `docs/aes_verbose_trace_fips197.json`, `docs/verbose_mode.md`, `api_server/tests/test_aes_verbose.py`
- Image-integrity notes: 纯数据热图；无人工改图
- Reviewer risk: trace 暴露中间状态，只应用于教学模式；timing 不应解释为稳定性能基准
- Data source: 项目保存的 FIPS 197 AES verbose JSON
- Script: `scripts/figures/plot_aes_verbose_trace.py`
- Outputs:
  - `docs/report_assets/figures/fig5_aes_verbose_trace.svg`
  - `docs/report_assets/figures/fig5_aes_verbose_trace.png`
  - `docs/report_assets/data/fig5_aes_verbose_trace.csv`
- Reproducible command: `.\.venv\Scripts\python.exe scripts\figures\plot_aes_verbose_trace.py`

## Figure 6

- `figure_id`: Fig. 6
- 中文标题：安全演示效果图
- English short title: Security demo results
- Backend: Python / matplotlib
- Core conclusion: 可脚本复现的安全 demo 显示 ECB 会保留图像块重复模式，而 PBKDF2 耗时随迭代次数近似线性上升。
- Figure archetype: image plate + quant
- Target journal/output: Nature-style double-column report figure, SVG + PNG
- Final size: 183 mm × 130 mm
- Panel map:
  - A: synthetic patterned source image
  - B: AES-ECB encrypted image
  - C: AES-CBC encrypted image
  - D: duplicate block ratio 对比
  - E: PBKDF2 iterations vs duration_ms log-scale curve
- Evidence hierarchy:
  - Hero evidence: Panels A-C 是可复现实验图像结果
  - Validation evidence: Panel D 量化 ECB 重复块泄漏
  - Controls/robustness: Panel E 来自真实 PBKDF2 计时，多次重复
- Statistics needed: PBKDF2 每个 iteration 多次重复，记录 mean/min/max；ECB ratio 来自实际密文 block 计数
- Source data needed: `api_server/app/services/demos_service.py` 或直接调用相同 Rust core 逻辑
- Image-integrity notes: 源图由脚本确定性生成；加密图为真实 AES 输出映射为 RGB
- Reviewer risk: synthetic 图像用于突出重复块泄漏，不代表自然图像全部同等明显
- Data source: 真实 AES/PBKDF2 脚本运行输出
- Script: `scripts/figures/plot_security_demos.py`
- Outputs:
  - `docs/report_assets/figures/fig6_security_demos.svg`
  - `docs/report_assets/figures/fig6_security_demos.png`
  - `docs/report_assets/data/fig6_ecb_leak_metrics.csv`
  - `docs/report_assets/data/fig6_pbkdf2_iterations.csv`
- Reproducible command: `.\.venv\Scripts\python.exe scripts\figures\plot_security_demos.py`

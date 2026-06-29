# CryptoLab 报告资产映射

生成时间：2026-06-29 Asia/Shanghai  
当前 `HEAD`：`0861103477a7126599bde0fafafb1a3ed602a9d3`  
阶段：阶段 1，仅建立资产与章节映射，不撰写正文，不生成 `.tex`，不编译 PDF。  

## 1. 使用原则

本映射以 `docs/report_assets/STATS.md` 为最高优先级事实底盘，并辅以 `docs/PROGRESS.md`、`docs/PROGRESS_DELTA.md`、`docs/report_assets/FRONT_SCREENSHOT_CLASSIFICATION.md`、`docs/report_assets/SCREENSHOT_INDEX.md`、`docs/report_assets/FIGURE_INDEX.md`、`docs/report_assets/FIGURE_QA.md`、`docs/report_assets/data/*.csv` 与 `docs/report_assets/logs/*`。若旧设计方案中的描述与最新统计材料冲突，例如 UTF-8 是否完成、benchmark 是否仅支持 SHA-256、demo 占位是否清理，应以最新统计材料、CSV、源码扫描和日志为准。

报告正文应优先插入 `docs/report_assets/figures/` 中 QA PASS 的实验图，以及 `docs/report_assets/screenshots/frontend/` 中已经归档的前端截图。API、测试、数据库和 Docker 目前主要是日志证据，若后续需要视觉截图，应按 `SCREENSHOT_CHECKLIST.md` 补拍，不应把失败日志改写成成功证据。

## 2. 全局事实资产

| 资产类别 | 路径 | 状态 | 用途 |
|---|---|---|---|
| 最新统计汇总 | `docs/report_assets/STATS.md` | 存在 | 代码规模、算法状态、API、测试、图表、截图和缺口总览 |
| 进度评估 | `docs/PROGRESS.md` | 存在 | 项目历史进度、算法层/接口层/数据层/前端/部署风险 |
| 阶段 A 清尾巴 | `docs/PROGRESS_DELTA.md` | 存在 | demo 占位清理、CLAUDE 更新、前端 `npm test`、Docker build 失败原因 |
| 交叉验证矩阵 | `docs/cross_validation_matrix.md` | 存在 | 第 4 章正确性验证主表 |
| AES verbose 文档 | `docs/verbose_mode.md` | 存在 | AES 教学模式文字证据 |
| AES verbose JSON | `docs/aes_verbose_trace_fips197.json` | 存在 | FIPS 197 中间状态数据源 |
| 源码索引 | `docs/report/source_index.md` | 已生成 | 后续正文引用源码和行号的主索引 |

## 3. 实验图资产

| 图号 | 标题 | 图片路径 | 数据路径 | QA 状态 | 推荐章节 |
|---|---|---|---|---|---|
| 图 4-1 | 测试验证总览图 | `docs/report_assets/figures/fig1_validation_overview.png` | `docs/report_assets/data/fig1_validation_overview.csv` | PASS | 4.1、4.2 |
| 图 3-1 | 算法覆盖与实现状态矩阵 | `docs/report_assets/figures/fig2_algorithm_coverage_matrix.png` 或 `fig2_algorithm_coverage_refined.png` | `docs/report_assets/data/fig2_algorithm_coverage_matrix.csv`；`fig2_algorithm_coverage_refined.csv` | PASS | 3.1、3.6、6.1 |
| 图 4-2 | 交叉验证证据矩阵 | `docs/report_assets/figures/fig3_cross_validation_evidence.png` 或 `fig3_cross_validation_refined.png` | `docs/report_assets/data/fig3_cross_validation_evidence.csv`；`fig3_cross_validation_refined.csv` | PASS | 4.2 |
| 图 4-16 | Benchmark 性能结果图 | `docs/report_assets/figures/fig4_benchmark_performance.png` | `docs/report_assets/data/fig4_benchmark_raw.csv`；`fig4_benchmark_summary.csv` | PASS | 4.5 |
| 图 4-15 | AES verbose trace 结果图 | `docs/report_assets/figures/fig5_aes_verbose_trace.png` | `docs/report_assets/data/fig5_aes_verbose_trace.csv`；`docs/aes_verbose_trace_fips197.json` | PASS | 4.4、3.4.1 |
| 图 4-17 | 安全演示效果图 | `docs/report_assets/figures/fig6_security_demos.png` | `docs/report_assets/data/fig6_ecb_leak_metrics.csv`；`fig6_pbkdf2_iterations.csv` | PASS | 4.6 |

说明：SVG 文件同目录存在，可在后续排版阶段替换 PNG。当前阶段只要求 Markdown 主稿规划，因此正文阶段可先引用 PNG，保留 SVG 作为高质量替代。

## 4. 前端截图资产

| 报告内容 | 推荐截图 | 当前状态 | 正文章节 | 说明 |
|---|---|---|---|---|
| 首页/主工作台 | `docs/report_assets/screenshots/frontend/P0_01_frontend_dashboard.png` | 已归档 | 4.3.1 | 控制台首页、导航、统计卡片、Recent activity |
| AES-GCM 加密成功 | `docs/report_assets/screenshots/frontend/P0_02_frontend_symmetric_aes_gcm_encrypt.png` | 已归档 | 4.3.2 | 对称加密结果，含密文、Hex、Tag |
| AES verbose 前端过程 | `docs/report_assets/screenshots/frontend/P0_03_frontend_symmetric_aes_verbose_trace.png` | 未发现 | 4.4 | 需补拍；当前用图 4-15、JSON、文档替代 |
| 哈希多算法摘要 | `docs/report_assets/screenshots/frontend/P0_04_frontend_hash_multi_digest.png` | 已归档 | 4.3.3 | SHA/RIPEMD 多摘要展示 |
| HMAC-SHA256 | `docs/report_assets/screenshots/frontend/P0_05_frontend_hmac_sha256.png` | 已归档 | 4.3.3 | HMAC 输入输出和 MAC 值 |
| PBKDF2 派生密钥 | `docs/report_assets/screenshots/frontend/P0_06_frontend_pbkdf2_derive.png` | 已归档 | 4.3.3 | 迭代参数和派生密钥 |
| RSA-1024 操作 | `docs/report_assets/screenshots/frontend/P0_07_frontend_rsa_operation.png` | 已归档 | 4.3.4 | RSA 密钥、加密或签名结果 |
| ECB 图像泄露 Demo | `docs/report_assets/screenshots/frontend/P0_08_frontend_demos_ecb_leak.png` | 已归档 | 4.6 | 前端漏洞演示主截图 |
| 审计日志列表 | `docs/report_assets/screenshots/frontend/P0_09_frontend_audit_logs.png` | 已归档 | 4.3.5、4.7 | 审计表、热力图、状态码 |
| Benchmark 前端结果 | `docs/report_assets/screenshots/frontend/P1_01_frontend_benchmark_results.png` | 已归档 | 4.5 | 前端性能结果展示 |
| 安全文件传输发送流程 | `docs/report_assets/screenshots/frontend/P1_02_frontend_secure_file_transfer_send.png` | 已归档 | 4.7 | envelope JSON 与协议步骤 |
| ECDSA k 复用 demo 结果 | `docs/report_assets/screenshots/frontend/extra/P0_08c_frontend_demo_ecdsa_k_reuse_result.png` | 已归档 | 4.6 | 前端展示共享 nonce 签名后的私钥恢复结果 |
| PBKDF2 迭代影响 demo | `docs/report_assets/screenshots/frontend/extra/P0_08d_frontend_demo_pbkdf2_impact.png` | 已归档 | 4.6 | 前端展示迭代次数与派生耗时对比 |
| 安全文件传输接收流程 | `docs/report_assets/screenshots/frontend/extra/P1_02b_frontend_secure_file_transfer_receive.png` | 已归档 | 4.7 | 接收方 envelope 输入、私钥解包与验签入口 |
| 安全文件传输验证结果 | `docs/report_assets/screenshots/frontend/extra/P1_02c_frontend_secure_file_transfer_result.png` | 已归档 | 4.7 | 接收端解密、摘要校验和签名验证结果 |
| 密钥管理 | `docs/report_assets/screenshots/frontend/P1_03_frontend_keys_store.png` | 已归档 | 4.3.5、5.4 | 密钥列表和详情 |
| ECDSA 签名/验签 | `docs/report_assets/screenshots/frontend/P1_04_frontend_ecdsa_sign_verify.png` | 已归档 | 4.3.4 | secp160r1 签名和验签 |
| Base64/UTF-8 编码转换 | `docs/report_assets/screenshots/frontend/P1_05_frontend_encoding_base64_utf8.png` | 已归档 | 4.3.5 | 编码转换输入输出 |
| 审计详情抽屉 | `docs/report_assets/screenshots/frontend/P1_06_frontend_audit_detail_drawer.png` | 已归档 | 4.3.5、5.6 | trace_id、hash、状态码、耗时 |

前端补充截图可按版面选用 `docs/report_assets/screenshots/frontend/extra/*.png`。其中 ECDSA k 复用、PBKDF2 迭代影响、安全文件接收流程和安全文件验证结果已经进入第 4 章正文；Dashboard catalog、AES 解密、Hash 顶部结果、RSA keygen/encrypt 和 Benchmark 明细仍作为可选补充图。第 4 章正文必须在每张图下写 80-150 字解读。

## 5. CSV 数据资产

| 数据表 | 路径 | 推荐章节 | 关键用法 |
|---|---|---|---|
| 算法实现表 | `docs/report_assets/data/algorithm_implementation.csv` | 3.1、3.2-3.5、6.3 | 15/15 有实现证据，14 个 已完成 (Complete)，RC6 为 部分完成 (Partial) |
| API 端点表 | `docs/report_assets/data/api_endpoints.csv` | 5.2、附录 A | 32 个端点；demos 4 项未显式 response_model |
| 代码规模表 | `docs/report_assets/data/code_lines_summary.csv` | 2.1、6.1 | Rust、API、测试、前端、文档、脚本规模 |
| 证据清单 | `docs/report_assets/data/evidence_inventory.csv` | 全文、附录 D/E/F | 报告资产和缺口索引 |
| 测试汇总 | `docs/report_assets/data/test_summary.csv` | 4.2、6.3 | Rust、API、前端、Docker 结果 |
| 测试向量来源 | `docs/report_assets/data/test_vector_sources.csv` | 3.2-3.5、4.2、附录 C | RFC/NIST/GB/T/权威库向量来源 |
| 状态码表 | `docs/report_assets/data/status_codes.csv` | 5.3、附录 B | 28 项业务状态码和 HTTP 映射 |
| 图表资产汇总 | `docs/report_assets/data/figure_assets_summary.csv` | 附录 D | 图号、源数据、脚本、QA 状态 |
| Benchmark 原始数据 | `docs/report_assets/data/fig4_benchmark_raw.csv` | 4.5 | 5 次重复测量 raw data |
| Benchmark 汇总 | `docs/report_assets/data/fig4_benchmark_summary.csv` | 4.5 | mean/median/min/max/n，分面比较 |
| AES verbose 数据 | `docs/report_assets/data/fig5_aes_verbose_trace.csv` | 4.4 | round-level state/timing |
| 安全 demo 数据 | `docs/report_assets/data/fig6_ecb_leak_metrics.csv`；`fig6_pbkdf2_iterations.csv` | 4.6 | ECB 重复块比例和 PBKDF2 迭代耗时 |

## 6. 日志证据资产

| 日志 | 路径 | 推荐章节 | 关键结论 |
|---|---|---|---|
| Git HEAD | `docs/report_assets/logs/git_head.txt` | 0、附录 F | 材料生成时为 `7a1c3f...`，当前 `HEAD` 已为 `0861103...` |
| Git status | `docs/report_assets/logs/git_status.txt` | 0、附录 F | 材料生成时工作树 dirty；当前核对为 clean |
| Rust 测试 | `docs/report_assets/logs/cargo_test_full.txt`；`cargo_test_tail.txt` | 4.2 | `53 passed, 0 failed, 3 ignored` |
| API 裸 pytest | `docs/report_assets/logs/pytest_full.txt` | 4.2、6.3 | 裸环境缺 `jwt`，不可写成通过 |
| API `.venv` pytest | `docs/report_assets/logs/pytest_venv_full.txt`；`pytest_venv_tail.txt` | 4.2 | `254 passed, 1 deselected` |
| 前端 npm test | `docs/report_assets/logs/npm_test_full.txt`；`npm_test_tail.txt` | 4.2 | TypeScript smoke check 通过 |
| Docker config | `docs/report_assets/logs/docker_compose_config.txt` | 2.2、6.3、附录 F | compose config 解析通过 |
| Docker build | `docs/report_assets/logs/docker_compose_build.txt`；`docs/progress_evidence/docker_build_stage_a.log` | 6.3、附录 F | build 失败，需按日志原因陈述 |
| 端点扫描 | `docs/report_assets/logs/endpoint_scan.txt` | 5.2 | 端点、handler、schema、测试证据扫描 |
| 状态码扫描 | `docs/report_assets/logs/status_code_scan.txt` | 5.3 | 状态码引用证据 |
| 测试向量扫描 | `docs/report_assets/logs/test_vector_sources_scan.txt` | 4.2、附录 C | 标准/测试向量来源扫描 |
| API 探测 | `docs/report_assets/logs/screenshots/api_probe_noproxy.txt` | 5.5 | OpenAPI `path_count=32`，SHA-256 API 响应 `code=1000` |
| 数据库快照 | `docs/report_assets/logs/screenshots/database_snapshot.txt` | 2.4、4.7、6.3 | 根 DB 行数：users、key_store、operation_logs 有数据，algorithm_metrics 稀疏或为 0 |

## 7. 分章资产映射

### 第 1 章 引言

| 小节 | 必备资产 | 说明 |
|---|---|---|
| 1.1 背景与意义 | 外部文献 [Heartbleed, Cloudbleed, ROCA, PS3 ECDSA] | 需正文阶段按 IEEE 编号引用真实文献 |
| 1.2 国内外现状 | OpenSSL、BoringSSL、RustCrypto、国密标准文献 | 不使用项目图表，主要使用参考文献 |
| 1.3 课题任务与挑战 | `..\网络信息安全密码算法编程-期中作业-要求及评分细则.md`；`algorithm_implementation.csv` | 对齐 15 种算法和 4 大类别 |
| 1.4 主要工作 | `STATS.md` 总览表 | 5 条贡献点，避免营销话术 |
| 1.5 报告组织结构 | Mermaid 章节关系图 | 正文阶段手写 Mermaid，不需额外图片 |

### 第 2 章 系统设计

| 小节 | 图表/数据/源码 | 说明 |
|---|---|---|
| 2.1 需求分析 | 课程评分细则、`STATS.md`、`code_lines_summary.csv` | FR/NFR 分表 |
| 2.2 总体架构 | Mermaid 六层架构图；`source_index.md` 第 2 节 | 架构图用 Mermaid 源码嵌入 |
| 2.3 ADR | `source_index.md` 第 2 节；`STATS.md`；外部工程文献 | 至少 4 个 ADR，每个含权衡矩阵 |
| 2.4 数据库设计 | `models/*.py`、`database_snapshot.txt`、`PROGRESS.md` | 四张核心表和当前本地数据状态 |
| 2.5 安全设计 | `kek.py`、`auth.py`、`rate_limit.py`、`audit.py`、`trace.py` | STRIDE、信任边界、密钥生命周期 |
| 2.6 权衡 | `status_codes.csv`、源码索引 | fail-closed、最小信任、职责分离 |

### 第 3 章 算法实现

| 小节 | 图表/数据/源码 | 说明 |
|---|---|---|
| 3.1 工程结构 | `rust_core/src/traits.rs`、`ffi.rs`、`algorithm_implementation.csv`、图 3-1 | Cargo workspace、PyO3、maturin、依赖隔离 |
| 3.2 编码 | `base64.rs`、`utf8.rs`、`test_vector_sources.csv` | Base64/UTF-8 的 5 段式结构 |
| 3.3 哈希 | `sha1.rs`、`sha2.rs`、`sha3.rs`、`ripemd.rs`、`hmac.rs`、`pbkdf2.rs` | SHA-1 安全态势、HMAC、PBKDF2 |
| 3.4 对称加密 | `aes.rs`、`sm4.rs`、`rc6.rs`、`modes/*.rs`、图 4-15 | AES 公式和 trace、SM4/AES 对比、RC6 限制 |
| 3.5 公钥密码 | `bigint/mod.rs`、`rsa.rs`、`ecc.rs`、`ecdsa.rs` | RSA/OAEP/PSS、ECC/ECDSA、RFC 6979 |
| 3.6 横切关注点 | `hmac.rs`、`gcm.rs`、`security.py`、`kek.py` | 常时间、密钥保护、内存安全边界 |

### 第 4 章执行结果、系统展示与性能分析

| 小节 | 图表/截图/数据 | 说明 |
|---|---|---|
| 4.1 测试体系 | 图 4-1、图 4-2、`cross_validation_matrix.md` | 三重验证体系 |
| 4.2 正确性验证 | `test_summary.csv`、`test_vector_sources.csv`、测试日志 | Rust/API/frontend 结果，区分裸 pytest 失败 |
| 4.3 前端展示 | P0/P1 前端截图 14 张 | 每图后写 80-150 字解读 |
| 4.4 AES verbose | 图 4-15、`verbose_mode.md`、JSON | 前端 P0-03 缺失需说明 |
| 4.5 性能基准 | 图 4-16、`fig4_benchmark_raw.csv`、`fig4_benchmark_summary.csv`、P1-01 | 分面比较，不用单一坐标轴混排 |
| 4.6 安全 demo | 图 4-17 至图 4-20、P0-08、P0-08c、P0-08d、Fig.6 | ECB、ECDSA k reuse、RSA 小指数、PBKDF2，含前端交互截图与汇总数据图 |
| 4.7 综合场景 | P1-02、P1-02b、P1-02c、`scenario_service.py` | 安全文件传输发送、接收与验证结果的端到端流程 |

### 第 5 章接口设计与调用

| 小节 | 资产 | 说明 |
|---|---|---|
| 5.1 设计原则 | `api_endpoints.csv`、`status_codes.csv` | RESTful、版本化、幂等、错误码 |
| 5.2 端点全景 | `api_endpoints.csv` | 32 项分类表，demos response_model 局限需承认 |
| 5.3 响应结构与状态码 | `schemas/common.py`、`status_codes.csv` | 统一响应与 28 个状态码 |
| 5.4 鉴权限流审计 | `auth.py`、`rate_limit.py`、`audit.py`、`key_service.py` | JWT、Redis、审计字段 |
| 5.5 调用范式 | `api_probe_noproxy.txt`、Swagger 待补拍、前端 API 模块 | curl/Python/Swagger/React |
| 5.6 可观测性 | `trace.py`、`metrics_service.py`、`database_snapshot.txt` | trace_id、异常处理、metrics 限制 |

### 第 6 章总结与展望

| 小节 | 资产 | 说明 |
|---|---|---|
| 6.1 工作总结 | `STATS.md`、图 3-1、图 4-1 | 回应 1 章目标 |
| 6.2 创新点 | 前端截图、AES verbose、demo 图、KEK、交叉验证图 | 每项 150-200 字展开 |
| 6.3 局限性 | `algorithm_implementation.csv`、Docker 日志、截图索引、pytest 日志、database_snapshot、api_endpoints | 至少 6 项，必须诚实写 |
| 6.4 未来工作 | 缺口表和 checklist | Docker、UI 自动化、metrics、更多 demo、排版 |

### 第 7 章参考文献与附录

| 部分 | 资产 | 说明 |
|---|---|---|
| 参考文献 | 正文阶段建立 IEEE 编号引用 | 至少 40 篇，全部正文出现 |
| 附录 A | `api_endpoints.csv` | 完整 32 端点 |
| 附录 B | `status_codes.csv` | 完整状态码 |
| 附录 C | `test_vector_sources.csv` | 测试向量来源 |
| 附录 D | `figure_assets_summary.csv`、`FIGURE_INDEX.md`、`FIGURE_QA.md` | 图表资产索引 |
| 附录 E | `SCREENSHOT_INDEX.md`、`FRONT_SCREENSHOT_CLASSIFICATION.md` | 截图资产索引 |
| 附录 F | `STATS.md` 复现命令、日志目录 | 构建与运行说明 |

## 8. 当前缺口暂存

以下缺口将在阶段 5 的 `REPORT_CHECKLIST.md` 中正式登记；阶段 1 先作为写作风险提醒：

| 缺口 | 当前状态 | 处理策略 |
|---|---|---|
| AES verbose 前端截图 | `P0_03_frontend_symmetric_aes_verbose_trace.png` 未发现 | 第 4 章用图 4-15、JSON、`verbose_mode.md` 替代，并标注待补拍 |
| Swagger `/docs` 截图 | API 截图目录为空 | 第 5 章可引用 `api_probe_noproxy.txt`，截图列为待补拍 |
| API 成功响应 PNG | 只有日志 | 第 5 章可贴 JSON 示例并引用日志路径 |
| 测试 PNG | API/npm 有日志，Rust 当前截图日志不宜当通过图 | 第 4 章以日志证据为主 |
| 数据库/Docker PNG | 目录为空或只有日志 | 第 6 章诚实记录 Docker build 失败和 metrics 稀疏 |
| `.tex`/PDF | 本阶段不要求且不创建 | 后续若转换，只能作为 checklist 可选命令 |



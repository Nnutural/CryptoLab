# CryptoLab 报告源码索引

生成时间：2026-06-29 Asia/Shanghai  
项目根目录：`D:\Nnutural\Desktop\BUPT_6\SecureProgrammingTechnologyandCaseDevelopment\期中作业\CryptoLab`  
当前 `HEAD`：`0861103477a7126599bde0fafafb1a3ed602a9d3`  
当前 `git status --short`：无输出，当前工作树在本次核对时为 clean  

## 1. 索引口径

本索引服务于《CryptoLab：基于 Rust × Python 异构架构的密码算法工程实现与安全分析》阶段 2-5 的正文撰写。索引依据包括本轮实际命令 `git status --short`、`git rev-parse HEAD`、`rg -n "pub fn|fn |struct |impl " rust_core/src`、`rg -n "@router\.(get|post|put|delete|patch)|APIRouter|def " api_server/app`，以及 `docs/report_assets/STATS.md`、`docs/PROGRESS.md`、`docs/PROGRESS_DELTA.md`、`docs/report_assets/data/*.csv` 和 `docs/report_assets/logs/*`。需要注意的是，`STATS.md` 与部分资产索引内部记录的基线提交为 `7a1c3f60933c60fc682958059662b4a486733bc1`，当前仓库 `HEAD` 为 `0861103477a7126599bde0fafafb1a3ed602a9d3`；后续正文应把“当前命令事实”和“材料内记录事实”分开表述。

本索引只记录报告可引用的源文件、测试文件、数据表和日志证据，不新增代码实现，不改变算法行为。若后续正文需要 30-80 行 Rust 源码节选，应从本索引列出的候选行段中再精读并截取，且每段代码后补 200 字以上解读。若某一事实在旧设计方案和最新统计材料之间冲突，应优先采用 `docs/report_assets/STATS.md`、CSV、源码扫描和测试日志。

## 2. 第 2 章系统设计源码索引

| 报告小节 | 事实主题 | 源码或证据路径 | 关键行号或证据 | 用法 |
|---|---|---|---|---|
| 2.1 需求分析 | 课程算法范围与接口要求 | `..\网络信息安全密码算法编程-期中作业-要求及评分细则.md` | 课程要求列出 4 大类算法、接口调用、35 页以上 PDF 评分项 | 作为 FR/NFR 的外部约束来源 |
| 2.1 需求分析 | 项目规模、算法、API、测试总览 | `docs/report_assets/STATS.md` | 第 2、3、4、5、9 节 | 作为系统规模和完成状态的主证据 |
| 2.2 总体架构 | FastAPI 应用装配 | `api_server/app/main.py` | `create_app` 55；`healthz` 104；`health` 108 | 支撑接口层和中间件链路 |
| 2.2 总体架构 | PyO3 模块注册 | `rust_core/src/lib.rs` | `cryptolab_core` 41 | 支撑 Rust × Python 异构架构 |
| 2.2 总体架构 | FFI 函数注册 | `rust_core/src/ffi.rs` | `register` 19；`aes_encrypt` 98；`aes_encrypt_with_trace` 116；hash 230-327；encoding 345-361；RSA/ECC/ECDSA 374-598 | 支撑 L2 算法层到 L3/L4 Python 服务层的调用链 |
| 2.3 ADR-001 Rust | Rust 算法模块分布 | `rust_core/src/**` | `STATS.md` 统计 Rust core 29 文件、6093 行 | 对比 C/Go/Python 时使用的实现规模证据 |
| 2.3 ADR-002 PyO3 | Python 绑定边界 | `rust_core/src/ffi.rs` | 19-87 注册；98-116 AES；374-598 公钥和 demo 绑定 | 对比 `ctypes/cffi` 时说明类型转换和错误映射 |
| 2.3 ADR-003 FastAPI/SQLAlchemy | 路由层 | `api_server/app/routers/*.py` | 32 个端点见 `docs/report_assets/data/api_endpoints.csv` | 接口选型和端点全景 |
| 2.3 ADR-003 FastAPI/SQLAlchemy | DB session | `api_server/app/db/session.py` | `_engine_kwargs` 18；`init_engine` 30；`get_db` 54 | 说明 SQLite/PostgreSQL 适配 |
| 2.3 ADR-004 密钥保护 | KEK/HKDF/信封加密 | `api_server/app/core/kek.py` | HKDF 常量 16-18；`derive_kek` 47；`get_kek` 52；`envelope_encrypt` 74；`envelope_decrypt` 92；`key_id_to_aad` 106 | 密钥保护 ADR 的主实现证据 |
| 2.4 数据库设计 | 用户表 | `api_server/app/models/user.py` | `__tablename__` 19；字段 21-29 | DDL 摘要和字段表 |
| 2.4 数据库设计 | 密钥表 | `api_server/app/models/key_store.py` | `__tablename__` 23；字段 25-37 | KEK 加密入库与软删除 |
| 2.4 数据库设计 | 审计日志表 | `api_server/app/models/operation_log.py` | `__tablename__` 21；字段 23-38 | trace、输入/输出 hash、状态码和耗时 |
| 2.4 数据库设计 | 性能指标表 | `api_server/app/models/algorithm_metric.py` | `__tablename__` 16；字段 18-24 | metrics 局限性应结合本地表数据 |
| 2.4 数据库设计 | Redis/内存缓存 | `api_server/app/core/cache.py` | cache protocol 16-31；memory backend 44-85；redis backend 94-122；`create_cache` 126 | 限流和 JWT 黑名单后端 |
| 2.5 安全设计 | JWT 黑名单 | `api_server/app/middleware/auth.py` | 黑名单读取 83；`_is_public_path` 101；`_is_protected_path` 105 | 鉴权信任边界 |
| 2.5 安全设计 | 限流 key | `api_server/app/middleware/rate_limit.py` | `rate_limit:{ip}:{path_prefix}` 30；429 响应 37-49 | Redis 键模式与 fail-closed |
| 2.5 安全设计 | Trace ID | `api_server/app/middleware/trace.py` | 22-26 | 请求追踪与日志关联 |
| 2.5 安全设计 | 审计写入 | `api_server/app/middleware/audit.py` | `dispatch` 28；操作推断 92；算法推断 101 | 审计字段来源 |
| 2.6 设计原则 | 状态码体系 | `api_server/app/core/status_codes.py` | `StatusCode` 8；`DEFAULT_MESSAGES` 47；`HTTP_FOR_STATUS` 79 | fail-closed 与统一错误语义 |

## 3. 第 3 章算法实现源码索引

| 报告小节 | 算法/主题 | 源码路径 | 关键行号 | 测试/向量证据 | 代码节选候选 |
|---|---|---|---|---|---|
| 3.1 工程结构与构建系统 | Trait 抽象 | `rust_core/src/traits.rs` | `SymmetricCipher` 22-34；`EncryptionTrace` 43；`RoundState` 54；`HashAlgorithm` 72-82；`PublicKeyAlgorithm` 103-127 | `cargo_test_full.txt` | 22-54 可节选，说明统一抽象 |
| 3.1 工程结构与构建系统 | PyO3 注册 | `rust_core/src/ffi.rs` | `register` 19-87；`to_pybytes` 87 | `STATS.md` 公开符号 49 个历史证据 | 19-87 可节选，说明 FFI 边界 |
| 3.2.1 Base64 | RFC 4648 编码/解码 | `rust_core/src/encoding/base64.rs` | `encode` 8；`decode` 37；`decode_byte` 84 | `rfc4648_section_10_vectors` 107；`algorithm_implementation.csv` status 已完成 (Complete) | 8-96 可节选或改伪码 |
| 3.2.2 UTF-8 | RFC 3629 编/解码 | `rust_core/src/encoding/utf8.rs` | `encode` 9；`decode` 36；`tail` 123；`ranged_byte` 127 | `encode_matches_rfc3629_widths` 148；`decode_rejects_ill_formed...` 165；status 已完成 (Complete) | 36-139 可节选，说明非法序列拒绝 |
| 3.3.1 SHA-1 | FIPS 180-4 | `rust_core/src/hash/sha1.rs` | `Sha1` 22；`update` 47；`finalize` 75；`compress` 145 | `fips_180_4_classic_vectors` 196；`million_a_vector` 212 | 117-190 可节选，说明 padding 与压缩函数 |
| 3.3.2 SHA-256 | FIPS 180-4 SHA-2 | `rust_core/src/hash/sha2.rs` | `Sha256` 205；`update` 230；`finalize` 241；`compress256` 375；Σ 函数 506-531 | `sha256_nist_short_vectors` 574；`sha2_reference_validation_against_rustcrypto` 671 | 299-421 可节选，说明消息扩展和 64 轮 |
| 3.3.3 SHA-3 | FIPS 202 | `rust_core/src/hash/sha3.rs` | `sha3_256` 10；`sha3_512` 18 | `fips_202_sha3_256_vectors` 30；`fips_202_sha3_512_vectors` 42 | 不建议长节选，正文说明 crate 边界 |
| 3.3.4 RIPEMD-160 | RIPEMD-160 digest | `rust_core/src/hash/ripemd.rs` | `ripemd160` 10 | `original_ripemd160_vectors` 22 | 不建议长节选，列差异表 |
| 3.3.5 HMAC | RFC 2104 / RFC 4231 | `rust_core/src/hash/hmac.rs` | generic `hmac` 10；`hmac_sha1` 43；`hmac_sha256` 51；`verify_hmac_sha256` 59 | RFC 2202 测试 68；RFC 4231 测试 84；常时间路径测试 100 | 10-60 可节选，说明 ipad/opad 和 `ConstantTimeEq` |
| 3.3.6 PBKDF2 | RFC 8018 / SP 800-132 | `rust_core/src/hash/pbkdf2.rs` | `pbkdf2_hmac_sha256` 16 | known vectors 69；invalid params 87 | 16-64 可节选，说明 U1/Uj 链 |
| 3.4.1 AES | FIPS 197 + SP 800-38A/38D | `rust_core/src/symmetric/aes.rs` | `AesTrace` 20；`Aes` 113；`encrypt_block` 183；`decrypt_block` 208；`encrypt_block_with_trace` 268；`expand_key` 355；`mix_columns` 428；`gf_mul` 456 | ECB/CBC/CTR/GCM 测试 487-596；FIPS 197 trace 629 | 268-336 或 355-456 可节选 |
| 3.4.2 SM4 | GB/T 32907-2016 | `rust_core/src/symmetric/sm4.rs` | `Sm4` 49；`new` 102；`crypt_block` 149；`tau` 169；`t_round` 179；dispatch 204/217 | `gb_t_32907_appendix_a_single_block` 239；million iterations 251 | 98-184 可节选，说明轮函数和密钥扩展 |
| 3.4.3 RC6 | ECB/CBC 已实现，GCM 不暴露 | `rust_core/src/symmetric/rc6.rs` | `Rc6` 24；`new` 79；`encrypt_block` 118；`decrypt_block` 156；dispatch 229/242 | `rc6_paper_appendix_b_zero_vector` 264；`algorithm_implementation.csv` status 部分完成 (Partial) | 79-156 可节选，正文必须标注模式限制 |
| 3.4.4 工作模式 | ECB/CBC/CTR/GCM | `rust_core/src/modes/*.rs` | ECB 11/25；CBC 8/35；CTR 10；GCM 16/47/84/148；padding 30/43/78 | `modes` 测试 132-148；AES GCM 测试 561 | GCM 84-148 可节选，说明 GHASH |
| 3.5.1 大数运算 | Miller-Rabin、扩展欧几里得、模幂 | `rust_core/src/bigint/mod.rs` | `CryptoBigInt` 17；`mod_pow` 31；`mod_inverse` 43；`is_prime_miller_rabin` 79；`random_prime` 126 | self-check 172；prime test 180 | 31-134 可节选，说明 OS CSPRNG 与素性检测 |
| 3.5.2 RSA-1024 | RFC 8017、OAEP/PSS、CRT、盲化 | `rust_core/src/pubkey/rsa.rs` | `RsaKeyPair` 27；`generate` 48；`private_op_crt` 100；`private_op_crt_blinded` 113；`oaep_encode` 375；`pss_encode` 479；`mgf1_sha256` 569 | RSA tests 637-771；2 个慢测 ignored | 48-145 或 375-510 可节选 |
| 3.5.3 ECC-160 | SEC 2 secp160r1 | `rust_core/src/pubkey/ecc.rs` | `CurveParams` 15；`curve_params` 61；`keygen` 105；`scalar_mul` 124；`point_add` 193；`point_double` 225 | base point 302；order test 316 | 61-163 或 193-253 可节选 |
| 3.5.4 ECDSA | FIPS 186 / RFC 6979 | `rust_core/src/pubkey/ecdsa.rs` | `sign` 19；`verify` 53；`rfc6979_generate_k` 107；`hash_to_scalar` 162 | sign/verify 198；tampering 218 | 19-72 或 107-162 可节选 |
| 3.6.1 Rust 内存安全 | 安全边界 | `rust_core/src/error.rs`、`rust_core/src/**/*.rs` | 无 `todo!()`/`unimplemented!()` 命中见 `STATS.md` | `cargo_test_full.txt` | 正文以扫描和测试证据论证 |
| 3.6.2 常时间执行 | `subtle` / `compare_digest` | `rust_core/src/hash/hmac.rs`、`rust_core/src/modes/gcm.rs`、`api_server/app/core/security.py`、`api_server/app/services/scenario_service.py` | HMAC 3/59；GCM 10；password verify 78；digest compare 182 | `verify_hmac_sha256_uses_constant_time_compare_path` 100 | HMAC 或 GCM 片段可节选 |
| 3.6.3 密钥生命周期 | `zeroize` 与服务端生命周期 | `rust_core/Cargo.toml`、`api_server/app/core/kek.py`、`api_server/app/services/key_service.py` | `zeroize` 依赖需正文前再核对；KEK 47-101；key store 20-183 | `test_keys.py`、`STATS.md` | 以 KEK/信封加密为主，避免夸大零化覆盖 |

## 4. 第 4 章执行结果与展示证据索引

| 报告小节 | 证据主题 | 路径 | 关键事实 |
|---|---|---|---|
| 4.1 测试体系 | 测试验证总览图 | `docs/report_assets/figures/fig1_validation_overview.png`；`fig1_validation_overview.svg` | Fig.1 QA PASS，数据源 `fig1_validation_overview.csv` |
| 4.1 测试体系 | 三重验证矩阵 | `docs/cross_validation_matrix.md`；`docs/report_assets/figures/fig3_cross_validation_evidence.png` | KAT、库对照、HTTP/API 等多层证据 |
| 4.2 正确性验证 | 测试汇总 | `docs/report_assets/data/test_summary.csv` | Rust 53 passed/0 failed/3 ignored；API `.venv` 254 passed/1 deselected；frontend `npm test` 为 TypeScript smoke；Docker build 失败 |
| 4.2 正确性验证 | Rust 日志 | `docs/report_assets/logs/cargo_test_full.txt` | 可引用通过摘要，不使用 `screenshots/cargo_test_for_screenshot.txt` 当前失败日志当通过截图 |
| 4.2 正确性验证 | API 日志 | `docs/report_assets/logs/pytest_venv_full.txt` | `.venv` 下通过；裸 pytest 缺 `jwt`，见 `pytest_full.txt` |
| 4.2 正确性验证 | 前端测试日志 | `docs/report_assets/logs/npm_test_full.txt` | `tsc -b --pretty false` smoke check |
| 4.3 前端展示 | 首页/工作台 | `docs/report_assets/screenshots/frontend/P0_01_frontend_dashboard.png` | 已归档 |
| 4.3 前端展示 | AES-GCM | `docs/report_assets/screenshots/frontend/P0_02_frontend_symmetric_aes_gcm_encrypt.png` | 已归档 |
| 4.3 前端展示 | Hash/HMAC/PBKDF2 | `P0_04_frontend_hash_multi_digest.png`、`P0_05_frontend_hmac_sha256.png`、`P0_06_frontend_pbkdf2_derive.png` | 已归档 |
| 4.3 前端展示 | RSA/ECDSA/编码/密钥/审计 | `P0_07_frontend_rsa_operation.png`、`P1_04_frontend_ecdsa_sign_verify.png`、`P1_05_frontend_encoding_base64_utf8.png`、`P1_03_frontend_keys_store.png`、`P0_09_frontend_audit_logs.png`、`P1_06_frontend_audit_detail_drawer.png` | 已归档 |
| 4.4 AES verbose | 前端截图缺口 | `docs/report_assets/screenshots/frontend/P0_03_frontend_symmetric_aes_verbose_trace.png` | 当前未发现，正文需说明待补拍 |
| 4.4 AES verbose | 替代证据 | `docs/verbose_mode.md`；`docs/aes_verbose_trace_fips197.json`；`docs/report_assets/figures/fig5_aes_verbose_trace.png` | FIPS 197 中间状态对照 |
| 4.5 性能基准 | benchmark 图 | `docs/report_assets/figures/fig4_benchmark_performance.png`；`fig4_benchmark_summary.csv`；`fig4_benchmark_raw.csv` | 17 项 benchmark，分面比较 |
| 4.6 安全演示 | 漏洞 demo 图 | `docs/report_assets/figures/fig6_security_demos.png`；`fig6_ecb_leak_metrics.csv`；`fig6_pbkdf2_iterations.csv` | ECB 泄露、PBKDF2 迭代影响 |
| 4.6 安全演示 | demo service | `api_server/app/services/demos_service.py` | ECB 51；ECDSA k reuse 111；RSA low exponent 169；PBKDF2 impact 232 |
| 4.7 综合场景 | 安全文件传输截图 | `docs/report_assets/screenshots/frontend/P1_02_frontend_secure_file_transfer_send.png` | 已归档 |
| 4.7 综合场景 | 场景实现 | `api_server/app/services/scenario_service.py` | `secure_file_send` 34；`secure_file_receive` 105 |

## 5. 第 5 章接口设计与调用源码索引

| 报告小节 | 主题 | 源码或数据路径 | 关键行号或事实 |
|---|---|---|---|
| 5.1 接口设计原则 | RESTful 路由组织 | `api_server/app/routers/*.py` | 32 个端点，见 `api_endpoints.csv` |
| 5.2 端点全景 | 端点 CSV | `docs/report_assets/data/api_endpoints.csv` | 32 个端点；4 个 demos 路由 `response_model` 未显式声明，状态 部分完成 (Partial) |
| 5.3 统一响应 | APIResponse | `api_server/app/schemas/common.py` | `code`、`message`、`data`、`trace_id` 等字段 18-21 |
| 5.3 状态码 | 状态码 CSV | `docs/report_assets/data/status_codes.csv` | 28 项状态码，`OK=1000`，错误分为参数、密码操作、鉴权、密钥、服务端 |
| 5.4 鉴权 | JWT issue/decode | `api_server/app/core/security.py` | `issue_access_token` 28；`decode_access_token` 50；`hash_password` 61；`verify_password` 75 |
| 5.4 鉴权 | JWT middleware | `api_server/app/middleware/auth.py` | dispatch 55；黑名单 key 83；匿名/保护路径 101-105 |
| 5.4 限流 | RateLimitMiddleware | `api_server/app/middleware/rate_limit.py` | dispatch 19；key 模式 30；429 响应 37-49 |
| 5.4 审计 | AuditMiddleware | `api_server/app/middleware/audit.py` | dispatch 28；`AuditRecord` 写入路径 41-55；操作解析 92 |
| 5.5 curl/Python 调用 | API 探测日志 | `docs/report_assets/logs/screenshots/api_probe_noproxy.txt` | OpenAPI `path_count=32`，SHA-256 响应 `code=1000` |
| 5.5 Swagger UI | 截图缺口 | `docs/report_assets/screenshots/api/P0_10_api_docs_overview.png` | 当前未发现 PNG，应在 checklist 中标注待补拍 |
| 5.5 前端集成 | 前端 API 模块 | `frontend/src/api/*.ts` | 后续正文前可按具体接口补扫 |
| 5.6 可观测性 | trace ID | `api_server/app/middleware/trace.py` | 22-26，将 `X-Trace-Id` 写回响应头 |
| 5.6 metrics | Metrics service | `api_server/app/services/metrics_service.py` | `record` 34；`query_metrics` 105；`row_to_item` 133 |

## 6. 第 6 章总结、局限与展望证据索引

| 局限或展望点 | 证据路径 | 写作约束 |
|---|---|---|
| RC6 当前为部分完成 | `docs/report_assets/data/algorithm_implementation.csv`；`rust_core/src/symmetric/rc6.rs` 31/53/229/242 | 必须写“ECB/CBC 已实现，GCM 不暴露”，不可写成全模式完成 |
| Docker build 失败 | `docs/report_assets/logs/docker_compose_build.txt`；`docs/progress_evidence/docker_build_stage_a.log` | 当前材料包含 Cargo edition2024 或 apt 502 失败原因，正文应按具体日志说明，不写成成功 |
| AES verbose 前端截图缺失 | `SCREENSHOT_INDEX.md` U-01；`FRONT_SCREENSHOT_CLASSIFICATION.md` M-01 | 第 4 章可用 `fig5`、JSON、文档替代，但需标注前端截图待补拍 |
| 裸 pytest 缺 `jwt` | `docs/report_assets/data/test_summary.csv`；`pytest_full.txt` | 同时说明项目 `.venv` 下 pytest 通过 |
| metrics 表数据稀疏 | `SCREENSHOT_INDEX.md` L-08；`PROGRESS.md` 第 3 节 | 不夸大长期观测，只写具备模型、接口和短时采集能力 |
| demos 路由 response_model | `api_endpoints.csv` | 4 个 demos route 未显式声明 `response_model`，接口章节和局限性需承认 |

## 7. 后续正文阶段推荐源码节选清单

| 编号 | 建议放入章节 | 文件与行段 | 原因 |
|---|---|---|---|
| Code 3-1 | 3.1 工程结构 | `rust_core/src/ffi.rs:19-87` | 展示 PyO3 注册和函数暴露边界 |
| Code 3-2 | 3.3 HMAC | `rust_core/src/hash/hmac.rs:10-60` | 展示 RFC 2104 构造和常时间验证 |
| Code 3-3 | 3.3 PBKDF2 | `rust_core/src/hash/pbkdf2.rs:16-64` | 展示迭代链和派生块逻辑 |
| Code 3-4 | 3.4 AES | `rust_core/src/symmetric/aes.rs:355-456` | 展示密钥扩展、SubBytes、MixColumns 和 GF 乘法 |
| Code 3-5 | 3.4 SM4 | `rust_core/src/symmetric/sm4.rs:98-184` | 展示 32 轮结构、`tau` 和线性变换 |
| Code 3-6 | 3.5 RSA | `rust_core/src/pubkey/rsa.rs:48-145` | 展示密钥生成、CRT 私钥操作和盲化 |
| Code 3-7 | 3.5 ECC | `rust_core/src/pubkey/ecc.rs:124-163` | 展示 Montgomery ladder 形态的标量乘 |
| Code 3-8 | 3.5 ECDSA | `rust_core/src/pubkey/ecdsa.rs:107-162` | 展示 RFC 6979 确定性 `k` |

以上 8 段中，正文硬性要求至少 6 段 Rust 源码节选；建议优先采用 Code 3-1、3-2、3-3、3-4、3-6、3-8，并按版面补充 SM4/ECC。


# CryptoLab 截图索引

生成时间：2026-06-29 20:03:06 +08:00  
基于 commit hash：`7a1c3f60933c60fc682958059662b4a486733bc1`  
前端 URL：`http://localhost:5173`  
后端 URL：`http://127.0.0.1:8000`  

> 说明：前端截图来自用户手动截取的 `D:\Nnutural\Desktop\BUPT_6\SecureProgrammingTechnologyandCaseDevelopment\期中作业\pic\front`。本轮只将这些真实截图复制/转码并按报告用途命名到 `docs/report_assets/screenshots/frontend/`，未伪造画面，未修改原始 JPG。详细来源映射见 `docs/report_assets/FRONT_SCREENSHOT_CLASSIFICATION.md`。

## 1. 已采集截图

| 编号 | 文件 | 内容 | 采集方式 | 对应报告章节 | 证据日志 |
|---|---|---|---|---|---|
| P0-01 | `docs/report_assets/screenshots/frontend/P0_01_frontend_dashboard.png` | 控制台首页、导航、统计卡片 | 用户手动截图，归档转 PNG | 系统运行 | `FRONT_SCREENSHOT_CLASSIFICATION.md` |
| P0-02 | `docs/report_assets/screenshots/frontend/P0_02_frontend_symmetric_aes_gcm_encrypt.png` | AES-256-GCM 加密成功 | 用户手动截图，归档转 PNG | 对称加密 | `FRONT_SCREENSHOT_CLASSIFICATION.md` |
| P0-04 | `docs/report_assets/screenshots/frontend/P0_04_frontend_hash_multi_digest.png` | 多算法哈希摘要结果 | 用户手动截图，归档转 PNG | 哈希模块 | `FRONT_SCREENSHOT_CLASSIFICATION.md` |
| P0-05 | `docs/report_assets/screenshots/frontend/P0_05_frontend_hmac_sha256.png` | HMAC-SHA256 计算结果 | 用户手动截图，归档转 PNG | 消息认证 | `FRONT_SCREENSHOT_CLASSIFICATION.md` |
| P0-06 | `docs/report_assets/screenshots/frontend/P0_06_frontend_pbkdf2_derive.png` | PBKDF2 派生密钥结果 | 用户手动截图，归档转 PNG | 密钥派生 | `FRONT_SCREENSHOT_CLASSIFICATION.md` |
| P0-07 | `docs/report_assets/screenshots/frontend/P0_07_frontend_rsa_operation.png` | RSA-1024 运算结果 | 用户手动截图，归档转 PNG | 公钥密码 | `FRONT_SCREENSHOT_CLASSIFICATION.md` |
| P0-08 | `docs/report_assets/screenshots/frontend/P0_08_frontend_demos_ecb_leak.png` | ECB 图像泄露 Demo | 用户手动截图，归档转 PNG | 安全演示 | `FRONT_SCREENSHOT_CLASSIFICATION.md` |
| P0-09 | `docs/report_assets/screenshots/frontend/P0_09_frontend_audit_logs.png` | 审计日志列表和热力图 | 用户手动截图，归档转 PNG | 审计追踪 | `FRONT_SCREENSHOT_CLASSIFICATION.md` |
| P1-01 | `docs/report_assets/screenshots/frontend/P1_01_frontend_benchmark_results.png` | Benchmark 吞吐量图 | 用户手动截图，归档转 PNG | 性能评估 | `FRONT_SCREENSHOT_CLASSIFICATION.md` |
| P1-02 | `docs/report_assets/screenshots/frontend/P1_02_frontend_secure_file_transfer_send.png` | 安全文件传输发送方流程 | 用户手动截图，归档转 PNG | 综合实验 | `FRONT_SCREENSHOT_CLASSIFICATION.md` |
| P1-03 | `docs/report_assets/screenshots/frontend/P1_03_frontend_keys_store.png` | 密钥管理列表和详情 | 用户手动截图，归档转 PNG | 密钥管理 | `FRONT_SCREENSHOT_CLASSIFICATION.md` |
| P1-04 | `docs/report_assets/screenshots/frontend/P1_04_frontend_ecdsa_sign_verify.png` | ECDSA 签名/验签结果 | 用户手动截图，归档转 PNG | ECDSA | `FRONT_SCREENSHOT_CLASSIFICATION.md` |
| P1-05 | `docs/report_assets/screenshots/frontend/P1_05_frontend_encoding_base64_utf8.png` | Base64 编码转换结果 | 用户手动截图，归档转 PNG | 编码转换 | `FRONT_SCREENSHOT_CLASSIFICATION.md` |
| P1-06 | `docs/report_assets/screenshots/frontend/P1_06_frontend_audit_detail_drawer.png` | 审计日志详情抽屉 | 用户手动截图，归档转 PNG | 审计细节 | `FRONT_SCREENSHOT_CLASSIFICATION.md` |
| X-01 | `docs/report_assets/screenshots/manual_needed/front_contact_sheet.jpg` | 27 张原始前端截图联络图 | 本地图片拼版，用于人工核对 | 截图整理 | `pic/front` 原始文件 |

## 1.1 已采集日志证据

| 编号 | 文件 | 内容 | 采集方式 | 对应报告章节 | 关键结论 |
|---|---|---|---|---|---|
| L-01 | `docs/report_assets/logs/screenshots/api_probe_noproxy.txt` | healthz、OpenAPI summary、SHA-256 API 成功响应 | Python urllib 禁用代理直连 | API 文档与调用链 | `path_count=32`，hash 响应 `code=1000` |
| L-02 | `docs/report_assets/logs/screenshots/pytest_for_screenshot.txt` | API 测试结果 | `api_server\.venv\Scripts\python.exe -m pytest --tb=no -q` | 测试验证 | `254 passed, 1 deselected in 75.75s` |
| L-03 | `docs/report_assets/logs/screenshots/npm_test_for_screenshot.txt` | 前端 TypeScript smoke test | `npm test` | 前端验证 | `tsc -b --pretty false` 退出码 0 |
| L-04 | `docs/report_assets/logs/screenshots/cargo_test_for_screenshot.txt` | Rust 测试当前重跑输出 | `cargo test --manifest-path rust_core\Cargo.toml --no-fail-fast` | 测试验证 | 本轮失败，日志显示 Rust/MSVC 工具链与资源问题 |
| L-05 | `docs/report_assets/logs/screenshots/docker_compose_config_for_screenshot.txt` | Docker compose 解析配置 | `docker compose -f deploy\docker-compose.yml config` | 部署设计 | services 包含 postgres、redis、rust-builder、api、frontend、nginx |
| L-06 | `docs/report_assets/logs/screenshots/docker_info_for_screenshot.txt` | Docker daemon 信息 | `docker info` | 部署环境 | Docker daemon 可用，Docker Desktop 26.0.0 |
| L-07 | `docs/progress_evidence/docker_build_stage_a.log` | Stage A Docker build 完整输出 | 历史进度证据 | 部署限制 | build 失败于 Debian `python3-pip` apt 502 |
| L-08 | `docs/report_assets/logs/screenshots/database_snapshot.txt` | SQLite 表结构、行数、脱敏审计样例 | Python sqlite3 只读连接 | 数据库与审计 | 根 DB: users=8, key_store=16, operation_logs=28, algorithm_metrics=0 |
| L-09 | `docs/report_assets/logs/screenshots/database_discovery.txt` | 数据库字段和 DB 文件发现 | `rg` + `Get-ChildItem` | 数据库设计 | 发现根 DB、api_server DB、模型/迁移证据 |
| L-10 | `docs/report_assets/logs/screenshots/service_probe.txt` | 端口与服务探测 | netstat + PowerShell web cmdlets | 运行环境 | 8000/5173 有监听；PowerShell web cmdlets 受代理返回 502 |
| L-11 | `docs/report_assets/logs/screenshots/backend_8001_probe.txt` | 备用端口 uvicorn 探测 | 临时启动 8001 后停止 | 运行环境 | 进程启动成功，但 PowerShell 请求仍受代理 502 |

## 2. 前端人工截图计划

| 编号 | 建议文件 | 页面/路由 | 截图内容 | 样例输入/操作 | 必须出现的结果 | 对应报告章节 | 状态 |
|---|---|---|---|---|---|---|---|
| P0-01 | `docs/report_assets/screenshots/frontend/P0_01_frontend_dashboard.png` | `/dashboard` | 主工作台、导航结构、统计卡片、近期活动 | 登录后进入控制台 | 12 个功能入口和 Dashboard 卡片 | 系统运行 | 已归档用户截图 |
| P0-02 | `docs/report_assets/screenshots/frontend/P0_02_frontend_symmetric_aes_gcm_encrypt.png` | `/symmetric` | AES-GCM 加密成功 | AES-256/GCM，明文 `BUPT CryptoLab 2026`，生成密钥并加密 | 密文 Base64/Hex、Tag、运算成功 | 对称加密 | 已归档用户截图 |
| P0-03 | `docs/report_assets/screenshots/frontend/P0_03_frontend_symmetric_aes_verbose_trace.png` | `/symmetric` | AES verbose trace | AES/ECB，明文 `0011223344556677`，启用教学模式 | Round state、Before/After、Timing bar | 中间过程可视化 | 缺失，待补拍 |
| P0-04 | `docs/report_assets/screenshots/frontend/P0_04_frontend_hash_multi_digest.png` | `/hash` | 多算法 hash 结果 | 输入 `BUPT CryptoLab`，计算默认勾选算法 | SHA/RIPEMD digest hex | 哈希模块 | 已归档用户截图 |
| P0-05 | `docs/report_assets/screenshots/frontend/P0_05_frontend_hmac_sha256.png` | `/hmac-pbkdf2` HMAC tab | HMAC-SHA256 MAC 值 | Key `secret-key`，Message `BUPT message authentication` | MAC hex、HMAC-SHA256 | 消息认证 | 已归档用户截图 |
| P0-06 | `docs/report_assets/screenshots/frontend/P0_06_frontend_pbkdf2_derive.png` | `/hmac-pbkdf2` PBKDF2 tab | PBKDF2 派生密钥 | Password `correct horse battery staple`，Salt `bupt2026`，100000 次，32 字节 | derived_key hex、迭代次数 | 密钥派生 | 已归档用户截图 |
| P0-07 | `docs/report_assets/screenshots/frontend/P0_07_frontend_rsa_operation.png` | `/rsa` | RSA-1024 密钥生成与加密或签名 | 生成密钥，明文 `BUPT secure programming` | Key ID、密文 hex 或 signature_hex | 公钥密码 | 已归档用户截图 |
| P0-08 | `docs/report_assets/screenshots/frontend/P0_08_frontend_demos_ecb_leak.png` | `/demos` | 安全漏洞 Demo | ECB 图像泄露，默认示例和默认 key，点击运行 | 教学警告、对比结果、泄露提示 | 安全演示 | 已归档用户截图 |
| P0-09 | `docs/report_assets/screenshots/frontend/P0_09_frontend_audit_logs.png` | `/audit` | 审计热力图与日志表 | 完成若干操作后查询 | Trace ID、操作、算法、状态、耗时 | 审计追踪 | 已归档用户截图 |
| P1-01 | `docs/report_assets/screenshots/frontend/P1_01_frontend_benchmark_results.png` | `/benchmark` | benchmark 运行结果 | 保留默认算法，点击 Run | 吞吐量图、详细数据表 | 性能评估 | 已归档用户截图 |
| P1-02 | `docs/report_assets/screenshots/frontend/P1_02_frontend_secure_file_transfer_send.png` | `/scenarios` | 安全文件传输发送流程 | 先生成 RSA/ECC 密钥，输入 `Confidential BUPT report payload` | 协议步骤完成、安全信封输出 | 综合实验 | 已归档用户截图 |
| P1-03 | `docs/report_assets/screenshots/frontend/P1_03_frontend_keys_store.png` | `/keys` | 密钥列表与详情 | 生成多类密钥，筛选或搜索 `rsa` | key id、算法、类型、公钥材料按钮 | 密钥管理 | 已归档用户截图 |
| P1-04 | `docs/report_assets/screenshots/frontend/P1_04_frontend_ecdsa_sign_verify.png` | `/ecc` | ECDSA 签名/验签 | 消息 `BUPT ECDSA demo`，签名后验签 | r/s、valid true 或签名成功 | ECDSA | 已归档用户截图 |
| P1-05 | `docs/report_assets/screenshots/frontend/P1_05_frontend_encoding_base64_utf8.png` | `/encoding` | Base64/UTF-8 编码转换 | 输入 `CryptoLab 编码测试`，编码再解码 | Base64 输出和还原文本 | 编码转换 | 已归档用户截图 |
| P1-06 | `docs/report_assets/screenshots/frontend/P1_06_frontend_audit_detail_drawer.png` | `/audit` | 审计详情抽屉 | 点击任一操作行 | trace_id、状态码、输入/输出 hash | 审计细节 | 已归档用户截图 |

## 3. 未采集截图

| 编号 | 计划内容 | 原因 | 人工补拍步骤 | 相关日志 |
|---|---|---|---|---|
| U-01 | AES verbose trace | `pic/front` 中未发现前端 verbose trace 截图；已有 `docs/report_assets/figures/fig5_aes_verbose_trace.png` 可作替代证据 | 访问 `http://localhost:5173`，在 `/symmetric` 选择 AES/ECB/加密，输入正好 16 字节明文，勾选教学模式后补拍 | `FRONT_SCREENSHOT_CLASSIFICATION.md` |
| U-02 | Swagger `/docs` 页面截图 | 本轮只采集 API 日志，没有自动打开浏览器截图 | 打开 `http://127.0.0.1:8000/docs`，截图 API 分组 | `api_probe_noproxy.txt` |
| U-03 | API 成功响应截图 | 已有日志，仍需用户选择 Swagger 或 HTTP 客户端画面 | 执行 `POST /api/v1/hash/sha256`，body `{"data":"BUPT CryptoLab"}` | `api_probe_noproxy.txt` |
| U-04 | Rust 测试通过截图 | 本轮 `cargo test` 失败，不能作为通过截图 | 修复/切换 Rust 工具链后重跑，或在报告中引用 `docs/PROGRESS.md` 历史通过记录并说明日期 | `cargo_test_for_screenshot.txt`, `docs/PROGRESS.md` |
| U-05 | Docker build 成功截图 | Stage A build 真实失败于 apt 502，本轮未重跑 build | 如果需要成功证据，修复网络/mirror 后重跑 `docker compose -f deploy\docker-compose.yml build` | `docs/progress_evidence/docker_build_stage_a.log` |
| U-06 | metrics/dashboard 有数据截图 | 根目录 DB 当前 `algorithm_metrics=0`，Dashboard 性能趋势可能为空 | 先运行 `/benchmark` 或 benchmark API，让 metrics 写入，再截图 Dashboard/metrics | `database_snapshot.txt` |

## 4. 推荐放入 PDF 的截图顺序

1. 系统运行：P0-01 Dashboard，总览前端完成度和导航结构。
2. 核心算法功能：P0-02 AES-GCM，P0-03 AES verbose，P0-04 Hash，P0-05 HMAC，P0-06 PBKDF2。
3. 公钥与综合场景：P0-07 RSA，P1-04 ECDSA，P1-02 安全文件传输。
4. 安全演示与审计：P0-08 漏洞 Demo，P0-09 审计日志，P1-06 审计详情。
5. API 与测试：P0-10 Swagger，P0-11 API 成功响应，P0-13 pytest，P0-14 npm test。
6. 数据库与部署：P0-15 数据库审计快照，P1-08 compose config，P1-09 Docker build 失败证据。
7. 性能与统计图：P1-01 Benchmark 前端截图，直接插入 `docs/report_assets/figures/fig1` 到 `fig6`，不要重复截低质量终端图。

## 5. 截图质量检查

- 分辨率：桌面截图建议 `1440x1000`；移动端可选 `390x844`，但 PDF 主图优先桌面。
- 完整性：截图必须包含页面标题、关键输入、关键输出或命令结论，避免只截空白区域。
- 真实性：失败就标失败；本轮 Rust 测试失败、Docker build 历史失败都不能写成通过。
- 敏感信息：不要展示 JWT、密码、私钥、完整 key material、password_hash、salt。数据库截图只展示脱敏列和 hash。
- 证据对应：前端截图文件保存到 `docs/report_assets/screenshots/frontend/`，API/测试/数据库/Docker 截图分别保存到对应子目录。
- 图表复用：Fig.1-Fig.6 已有 SVG/PNG 和 QA PASS，实验结果优先插入图表资产，而不是终端截图。

# CryptoLab 报告截图清单

生成时间：2026-06-29 20:03:06 +08:00  
基于 commit hash：`7a1c3f60933c60fc682958059662b4a486733bc1`

## 1. 截图选择依据

本清单基于当前仓库真实文件和本轮命令输出整理。已核验的材料包括：

- 前端：`frontend/src/main.tsx`、`frontend/src/router/index.tsx`、`frontend/src/components/Shell.tsx`、`frontend/src/components/LoginView.tsx`、`frontend/src/components/nav.ts`、`frontend/src/views/*.tsx`、`frontend/src/api/*.ts`、`frontend/src/stores/auth.tsx`。当前前端是 React 18 + Vite + Tailwind，不存在旧提示中的 `App.vue` 和 Vue views。
- 后端：`api_server/app/main.py`、`api_server/app/routers/*.py`、`api_server/app/schemas/*.py`、`api_server/app/services/*.py`、`api_server/app/models/*.py`。OpenAPI 当前有 32 个 path，tags 为 `audit, auth, benchmark, demos, encoding, hash, keys, metrics, pubkey, scenarios, symmetric`。
- 测试与部署：`rust_core/**/*.rs`、`rust_core/Cargo.toml`、`api_server/tests/*.py`、`deploy/docker-compose.yml`、`deploy/Dockerfile.*`、`deploy/nginx.conf`。
- 进度与图表材料：`docs/PROGRESS.md`、`docs/PROGRESS_DELTA.md`、`docs/report_assets/FIGURE_INDEX.md`、`docs/report_assets/FIGURE_QA.md`、`docs/report_assets/figures/*`、`docs/progress_evidence/*`。
- 本轮新增日志：`docs/report_assets/logs/screenshots/` 下的 cargo、pytest、npm test、Docker config、Docker info、API 探测、服务探测和数据库快照日志。

前端页面截图不自动采集，全部标记为“待用户手动截图”。API、测试、数据库、Docker 类材料优先保留原始日志，截图建议只基于真实日志或真实页面，不伪造界面与结果。

## 2. P0 必拍截图

| 编号 | 截图名称 | 页面/命令 | 截图内容 | 样例输入/操作 | 预期画面 | 建议文件名 | 对应报告章节 | 采集方式 | 状态 |
|---|---|---|---|---|---|---|---|---|---|
| P0-01 | 前端主工作台 | `http://localhost:5173/dashboard` | 顶部栏、侧边导航、算法/密钥/审计/性能概览卡片、Recent activity | 先注册或登录测试账号；进入控制台 | 页面标题“控制台”或 Welcome back，侧边栏包含 12 个功能入口 | `P0_01_frontend_dashboard.png` | 系统运行与整体 UI | 用户手动截图，桌面 1440x1000 | 待用户手动截图 |
| P0-02 | AES-GCM 加密成功 | `/symmetric` | AES 参数区、密钥选择、明文、密文 Base64/Hex、Tag、耗时 | 算法 AES，密钥长度 AES-256，模式 GCM，明文 `BUPT CryptoLab 2026`，点击“生成新密钥”后“执行加密” | “运算成功”、算法 `AES-GCM`、密文 Base64、Hex 视图、认证标签 Tag | `P0_02_frontend_symmetric_aes_gcm_encrypt.png` | 对称加密功能 | 用户手动截图 | 待用户手动截图 |
| P0-03 | AES verbose trace | `/symmetric` | AES 教学模式 trace，Round state matrix，播放/上一步/下一步按钮，每轮耗时 | 算法 AES，模式 ECB，方向加密，明文 `0011223344556677`，启用“教学模式 (Verbose)”，点击“执行加密” | `AES-128/192/256 加密过程`、Round 0 Initial AddRoundKey、Before/After、每轮耗时 | `P0_03_frontend_symmetric_aes_verbose_trace.png` | AES 中间过程可视化 | 用户手动截图 | 待用户手动截图 |
| P0-04 | 多算法哈希计算 | `/hash` | SHA-1/SHA-256/SHA3-256/RIPEMD-160 多卡片结果 | 文本输入 `BUPT CryptoLab`，保留默认勾选算法，点击计算 | 各算法 digest hex、位数 Tag、雪崩效应提示或对比区 | `P0_04_frontend_hash_multi_digest.png` | 哈希算法覆盖 | 用户手动截图 | 待用户手动截图 |
| P0-05 | HMAC 计算结果 | `/hmac-pbkdf2` 的 HMAC tab | HMAC 输入、底层哈希选择、MAC hex 输出 | Key `secret-key`，Message `BUPT message authentication`，算法 SHA-256，点击计算 | `MAC 值`、`HMAC-SHA256`、MAC hex、耗时 | `P0_05_frontend_hmac_sha256.png` | 消息认证 | 用户手动截图 | 待用户手动截图 |
| P0-06 | PBKDF2 派生密钥 | `/hmac-pbkdf2` 的 PBKDF2 tab | 密码、盐、迭代次数滑块、derived_key hex | Password `correct horse battery staple`，Salt `bupt2026`，Iterations `100000`，KeyLen `32`，点击派生 | `derived_key (hex)`、迭代次数、长度 Tag；低迭代时会出现安全性告警 | `P0_06_frontend_pbkdf2_derive.png` | 密钥派生 | 用户手动截图 | 待用户手动截图 |
| P0-07 | RSA 公钥密码操作 | `/rsa` | RSA-1024 密钥对、公钥参数、加密或签名结果 | 点击“生成密钥对”；加密明文 `BUPT secure programming`，点击执行 | Key ID、模数/指数摘要、密文 hex 或 signature_hex、成功状态 | `P0_07_frontend_rsa_operation.png` | 公钥密码模块 | 用户手动截图 | 待用户手动截图 |
| P0-08 | 安全漏洞 Demo | `/demos` | 教学演示警告、Demo tab、攻击/对比结果 | 选择“ECB 图像泄露”，使用默认示例图像和默认 AES-128 key，点击运行 | 对比结果区出现 ECB/CBC 或泄露说明、重复块比例等结果 | `P0_08_frontend_demos_ecb_leak.png` | 漏洞 Demo | 用户手动截图 | 待用户手动截图 |
| P0-09 | 审计日志页面 | `/audit` | 今日操作热力图、过滤器、审计表格、Trace ID、状态码 | 先完成 AES/RSA/Hash 操作，再进入审计日志，点击“查询” | `今日操作热力分布`、表格列 Trace ID/操作/算法/用户/耗时/状态/时间，状态含 `1000 成功` 或真实错误 | `P0_09_frontend_audit_logs.png` | 审计追踪 | 用户手动截图 | 待用户手动截图 |
| P0-10 | FastAPI Swagger 总览 | `http://127.0.0.1:8000/docs` | Swagger UI 展示 API 分组和端点 | 浏览器打开 `/docs`；如 PowerShell 请求 502，浏览器仍优先使用本机直连或关闭代理 | 页面标题 `CryptoLab API`，能看到 auth/symmetric/hash/pubkey/demos/benchmark/metrics 等分组 | `P0_10_api_docs_overview.png` | API 文档 | 用户手动截图；日志见 `api_probe_noproxy.txt` | 待用户手动截图 |
| P0-11 | 关键 API 成功响应 | Swagger 或 HTTP 客户端：`POST /api/v1/hash/sha256` | 一次真实成功响应 JSON | Body: `{"data":"BUPT CryptoLab"}` | `code: 1000`、`digest_hex: 225b5f...32c0e`、`algorithm: sha256`、`trace_id` | `P0_11_api_hash_success_response.png` | API 调用链 | 可手动截图；已采集日志 | 已采集日志，待截图 |
| P0-12 | Rust 测试证据 | `cargo test --manifest-path rust_core\Cargo.toml --no-fail-fast` | 当前命令输出或历史通过证据 | 本轮命令已保存失败日志；历史 `docs/PROGRESS.md` 记录 `53 passed; 0 failed; 3 ignored` | 当前日志显示本机 Rust/MSVC 工具链失败；报告中不要把本轮结果写成通过 | `P0_12_tests_cargo_result.png` | 测试验证 | 截图日志或历史证据 | 需人工选择：当前失败日志或历史通过证据 |
| P0-13 | API pytest 通过 | `api_server\.venv\Scripts\python.exe -m pytest --tb=no -q` | pytest 进度点和汇总 | 已执行并保存日志 | `254 passed, 1 deselected in 75.75s` | `P0_13_tests_pytest_pass.png` | 测试验证 | 截图日志 | 已采集日志，待截图 |
| P0-14 | 前端 npm test 通过 | `Push-Location frontend; npm test; Pop-Location` | TypeScript smoke test 输出 | 已执行并保存日志 | `cryptolab-frontend@0.1.0 test` 和 `tsc -b --pretty false`，退出码 0 | `P0_14_tests_npm_test_pass.png` | 前端验证 | 截图日志 | 已采集日志，待截图 |
| P0-15 | 数据库审计快照 | `docs/report_assets/logs/screenshots/database_snapshot.txt` | 表结构、行数、脱敏 operation_logs 样例 | 直接打开日志或终端 `Get-Content` | 表 `users/key_store/operation_logs/algorithm_metrics`；根目录 DB 有 `operation_logs=28`；只展示 hash、trace_id、状态、耗时 | `P0_15_database_audit_snapshot.png` | 数据层与审计 | 截图日志 | 已采集日志，待截图 |

## 3. P1 建议截图

| 编号 | 截图名称 | 页面/命令 | 截图内容 | 样例输入/操作 | 预期画面 | 建议文件名 | 对应报告章节 | 采集方式 | 状态 |
|---|---|---|---|---|---|---|---|---|---|
| P1-01 | Benchmark 前端结果 | `/benchmark` | 算法选择、进度条、吞吐量图、详细数据表 | 保留默认选中 AES/SM4/RC6/SHA，点击“Run” | 吞吐量 MB/s、迭代次数、data size、耗时表格；若鉴权/网络失败则截图错误提示 | `P1_01_frontend_benchmark_results.png` | 性能评估 | 用户手动截图 | 待用户手动截图 |
| P1-02 | 安全文件传输发送流程 | `/scenarios` | RSA-OAEP + AES-GCM + SHA-256 + ECDSA 流程步骤和安全信封 | 先在 `/rsa` 和 `/ecc` 生成密钥；输入 `Confidential BUPT report payload`；点击“生成安全信封” | 协议流程步骤完成，输出 envelope JSON，标签显示机密性/完整性/不可否认性 | `P1_02_frontend_secure_file_transfer_send.png` | 综合场景 | 用户手动截图 | 待用户手动截图 |
| P1-03 | 密钥管理 | `/keys` | 密钥列表、类型过滤、选中密钥详情、公钥材料按钮 | 先生成 AES/RSA/ECC 密钥；搜索 `rsa` 或选择 RSA 公钥；点击某一行 | key id、algorithm、key type、created_at、public material 可查看但不显示私钥 | `P1_03_frontend_keys_store.png` | 密钥管理与 KEK | 用户手动截图 | 待用户手动截图 |
| P1-04 | ECDSA 签名与验签 | `/ecc` | secp160r1 密钥、公钥 Qx/Qy、r/s、验签结果 | 点击生成密钥；消息 `BUPT ECDSA demo`；签名后切到验签填入 r/s | `签名成功`，或验签 `valid true`；曲线 `secp160r1` | `P1_04_frontend_ecdsa_sign_verify.png` | ECC/ECDSA | 用户手动截图 | 待用户手动截图 |
| P1-05 | 编码转换 | `/encoding` | Base64/UTF-8 转换左右栏 | Plain Text `CryptoLab 编码测试`，点击编码；再点击解码 | Base64 输出、字节长度、编码/解码按钮状态 | `P1_05_frontend_encoding_base64_utf8.png` | 编码模块 | 用户手动截图 | 待用户手动截图 |
| P1-06 | 审计详情抽屉 | `/audit` | 点击一条日志后的详情抽屉 | 在审计表点击 AES 或 RSA 操作行 | 详情抽屉显示 trace_id、用户、操作、算法、状态、输入/输出 SHA-256 hash | `P1_06_frontend_audit_detail_drawer.png` | 审计追踪 | 用户手动截图 | 待用户手动截图 |
| P1-07 | OpenAPI 端点详情 | `/docs` 展开 `/api/v1/symmetric/{algo}/encrypt` 或 `/api/v1/benchmark/{algo}` | 请求 schema、响应 schema、鉴权标识 | 展开端点，不必执行敏感接口 | 能看到 path、schema、response model | `P1_07_api_docs_endpoint_detail.png` | API 设计 | 用户手动截图 | 待用户手动截图 |
| P1-08 | Docker compose config | `docker compose -f deploy\docker-compose.yml config` | compose 解析结果 | 已保存日志 | services 包含 postgres、redis、rust-builder、api、frontend、nginx | `P1_08_docker_compose_config.png` | 部署设计 | 截图日志 | 已采集日志，待截图 |
| P1-09 | Docker build 失败证据 | `docs/progress_evidence/docker_build_stage_a.log` | 真实构建失败关键错误 | 打开日志末尾 | `python3-pip` apt 下载 502，exit code 100；不能写成 build 成功 | `P1_09_docker_build_failure.png` | 部署限制 | 截图历史日志 | 有历史日志，待截图 |
| P1-10 | 论文级统计图资产 | `docs/report_assets/figures/` 和 `FIGURE_QA.md` | Fig.1-Fig.6 文件和 QA PASS | 打开目录或 QA 文档 | SVG/PNG/CSV 存在且 QA PASS | `P1_10_report_figures_qa.png` | 实验数据图 | 截图目录或文档 | 待用户手动截图 |

## 4. P2 可选截图

| 编号 | 截图名称 | 页面/命令 | 截图内容 | 样例输入/操作 | 预期画面 | 建议文件名 | 对应报告章节 | 采集方式 | 状态 |
|---|---|---|---|---|---|---|---|---|---|
| P2-01 | 登录/注册页面 | `/login` | 登录和注册切换、JWT 提示 | 注册 `report_user_20260629`，密码 `ReportDemo2026!`；密码框会被遮蔽 | CryptoLab 登录卡片、JWT/Bearer Token 提示、注册成功后回到登录 | `P2_01_frontend_login_register.png` | 鉴权流程 | 用户手动截图 | 可选，待手动截图 |
| P2-02 | 401/鉴权失败 | 清空 localStorage 后访问 `/keys` 或调用需登录 API | 重定向登录或 401 响应 | 浏览器无 token 访问受保护路由 | 前端跳转 `/login`，或 API 返回鉴权错误 | `P2_02_auth_required.png` | JWT 安全设计 | 用户手动截图 | 可选 |
| P2-03 | Redis/限流证据 | `api_server/app/middleware/rate_limit.py` 或接口高频请求日志 | 限流 key 模式与响应 | 不建议大量压测；可截图源码片段或进度证据 | `rate_limit:{ip}:{path_prefix}`、登录限流配置 | `P2_03_rate_limit_evidence.png` | 限流设计 | 文档或源码截图 | 可选 |
| P2-04 | Alembic 迁移历史 | `api_server/alembic/versions/*.py` | `0001_initial_schema.py` 和 `0002_fix_algorithm_metrics_schema.py` | 打开文件列表或终端列目录 | 迁移文件创建 users/key_store/operation_logs/algorithm_metrics | `P2_04_alembic_migrations.png` | 数据库设计 | 用户手动截图 | 可选 |
| P2-05 | README/报告目录结构 | `README.md`、`docs/report_assets/` | 开源仓库说明与报告资产目录 | 文件树或编辑器截图 | 能看到 README、figures、logs、screenshots、index/checklist | `P2_05_repo_docs_structure.png` | 交付材料 | 用户手动截图 | 可选 |
| P2-06 | Metrics API 或表数据 | `/metrics` 或 `database_snapshot.txt` | metrics 表和趋势数据 | 先运行 benchmark 以写入 metrics；再打开 Dashboard 或 API | 当前根 DB `algorithm_metrics=0`，`api_server/cryptolab.db` 有 1 条；截图前建议先运行 benchmark | `P2_06_metrics_after_benchmark.png` | 可观测性 | 条件满足后手动截图 | 可选，需先生成数据 |

## 5. 无需截图项

- 不建议逐个截图源码文件。报告中可引用路径和关键代码片段，截图会占页且信息密度低。
- 不建议截图私钥、JWT access token、密码哈希、salt、完整 key material。密钥管理截图只展示 key id、类型、算法、公钥材料或脱敏字段。
- 不建议用终端截图替代 `docs/report_assets/figures/` 中已经生成的 Fig.1-Fig.6 论文级图。实验结果优先直接插入 SVG/PNG。
- 不建议重复截图每一个 Swagger 端点。P0 拍总览，P1 只补一个关键端点详情即可。
- 不建议截图旧 Vue 路径或旧 README 描述。当前项目没有 Vue 文件，截图计划以 React 路由为准。
- 不建议把本轮失败的 `cargo test` 日志截成“通过”证据。若报告要写通过，必须引用 `docs/PROGRESS.md` 的历史通过记录或重新修复本机 Rust/MSVC 环境后重跑。

## 6. 手工补拍项

### 前端人工截图内容表

| 编号 | 页面名称 | 前端路由或 URL | 截图前准备 | 样例输入 | 点击/操作步骤 | 必须出现在截图中的 UI 元素 | 成功输出或错误输出 | 建议截图范围 | 建议文件名 | 对应报告章节 | 状态 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| F-01 | 首页/主工作台 | `http://localhost:5173/dashboard` | 后端 `8000` 与前端 `5173` 可访问；已登录 | 无 | 登录后进入 `/dashboard` | Header、Sidebar、Algorithms/Stored keys/Recent operations/Average latency | Dashboard 数据可为空，但导航结构必须完整 | 全页 | `P0_01_frontend_dashboard.png` | 系统运行 | 待用户手动截图 |
| F-02 | AES-GCM 成功加密 | `/symmetric` | 已登录 | `BUPT CryptoLab 2026` | 选 AES/AES-256/GCM，生成新密钥，点击执行加密 | 算法、密钥、IV、明文、运算结果卡片 | Base64/Hex/Tag、运算成功、耗时 | 全页或左右双栏 | `P0_02_frontend_symmetric_aes_gcm_encrypt.png` | 对称加密 | 待用户手动截图 |
| F-03 | AES verbose trace | `/symmetric` | 已登录；AES ECB 模式 | `0011223344556677` | 选 AES/ECB/加密，启用教学模式，执行 | AES trace viewer、Round 0、StateMatrix、Timing bar | Round state 和每轮耗时可见 | 结果区局部或全页 | `P0_03_frontend_symmetric_aes_verbose_trace.png` | 中间过程可视化 | 待用户手动截图 |
| F-04 | 哈希计算 | `/hash` | 已登录 | `BUPT CryptoLab` | 勾选 SHA-1/SHA-256/SHA3-256/RIPEMD-160，点击计算 | 输入文本、算法选择、摘要卡片 | 多个 digest hex | 全页 | `P0_04_frontend_hash_multi_digest.png` | 哈希模块 | 待用户手动截图 |
| F-05 | HMAC | `/hmac-pbkdf2` | 已登录；HMAC tab | Key `secret-key`，Message `BUPT message authentication` | 选 SHA-256，点击计算 | HMAC 输入区、MAC 值卡片 | MAC hex 和耗时 | 全页 | `P0_05_frontend_hmac_sha256.png` | 消息认证 | 待用户手动截图 |
| F-06 | PBKDF2 | `/hmac-pbkdf2` | 已登录；PBKDF2 tab | Password `correct horse battery staple`，Salt `bupt2026`，Iterations `100000`，KeyLen `32` | 切换 PBKDF2，填写参数，点击派生 | Iterations slider、derived_key | derived_key hex、迭代/长度 Tag | 全页 | `P0_06_frontend_pbkdf2_derive.png` | 密钥派生 | 待用户手动截图 |
| F-07 | RSA | `/rsa` | 已登录 | `BUPT secure programming` | 生成 RSA-1024 密钥；执行加密或签名 | RSA key card、Key ID、参数与结果区 | 密文 hex 或 signature_hex | 全页 | `P0_07_frontend_rsa_operation.png` | 公钥密码 | 待用户手动截图 |
| F-08 | 漏洞 Demo | `/demos` | 已登录 | 使用默认 Demo 参数 | 选择 ECB 图像泄露，点击运行 | 教学警告、Demo tab、演示参数、对比结果 | 结果图区和泄露/比例提示 | 全页 | `P0_08_frontend_demos_ecb_leak.png` | 安全演示 | 待用户手动截图 |
| F-09 | 审计日志 | `/audit` | 已完成几次算法操作 | 可筛选 AES 或全部状态 | 打开页面，点击查询；可选点击一行打开详情 | 热力图、过滤器、日志表格 | Trace ID、操作、算法、耗时、状态 | 全页 | `P0_09_frontend_audit_logs.png` | 审计追踪 | 待用户手动截图 |
| F-10 | Benchmark | `/benchmark` | 已登录；后端可访问 | 默认选中算法 | 点击 Run，等待完成 | 选择测试算法、进度条、吞吐量图、详细数据 | throughput、iterations、ms | 全页 | `P1_01_frontend_benchmark_results.png` | 性能评估 | 待用户手动截图 |
| F-11 | 安全文件传输 | `/scenarios` | 先生成 RSA 与 ECC 密钥 | `Confidential BUPT report payload` | 发送模式下点击生成安全信封 | 协议步骤、输出安全信封 | 机密性/完整性/不可否认性 Tag | 全页 | `P1_02_frontend_secure_file_transfer_send.png` | 综合实验 | 待用户手动截图 |
| F-12 | 密钥管理 | `/keys` | 已生成多类密钥 | 搜索 `rsa` 或过滤 RSA 公钥 | 打开页面，选中密钥，必要时点击查看公钥材料 | 密钥列表、类型 Tag、详情卡片 | 只展示公钥或脱敏信息，不显示私钥 | 全页或列表+详情 | `P1_03_frontend_keys_store.png` | 密钥安全 | 待用户手动截图 |
| F-13 | ECDSA | `/ecc` | 已登录 | `BUPT ECDSA demo` | 生成 secp160r1 密钥，签名，再验签 | 公钥 Qx/Qy、r/s、验签结果 | 签名成功或 valid true | 全页 | `P1_04_frontend_ecdsa_sign_verify.png` | ECDSA | 待用户手动截图 |
| F-14 | 编码转换 | `/encoding` | 已登录 | `CryptoLab 编码测试` | 点击编码，再点击解码 | 左右文本区、Base64/UTF-8 模式 | Base64 输出与还原文本 | 全页 | `P1_05_frontend_encoding_base64_utf8.png` | 编码转换 | 待用户手动截图 |
| F-15 | 审计详情抽屉 | `/audit` | 审计表有记录 | 无 | 点击任一操作行 | 右侧详情抽屉、trace_id、hash 字段 | 输入/输出 SHA-256 hash、状态码 | 局部或全页 | `P1_06_frontend_audit_detail_drawer.png` | 审计细节 | 待用户手动截图 |

### 非前端补拍项

- API Swagger 总览：浏览器打开 `http://127.0.0.1:8000/docs`，保存为 `docs/report_assets/screenshots/api/P0_10_api_docs_overview.png`。
- API 成功响应：Swagger 或 HTTP 客户端执行 `POST /api/v1/hash/sha256`，保存为 `docs/report_assets/screenshots/api/P0_11_api_hash_success_response.png`。已采集日志：`docs/report_assets/logs/screenshots/api_probe_noproxy.txt`。
- 测试结果：打开对应日志或重新运行命令后截图。API 和 npm test 本轮通过；Rust 本轮失败，不要截图成通过。
- 数据库审计：打开 `docs/report_assets/logs/screenshots/database_snapshot.txt`，截图表结构和脱敏 `operation_logs` 样例。
- Docker：截图 `docker_compose_config_for_screenshot.txt` 和 `docs/progress_evidence/docker_build_stage_a.log` 中的真实 compose config 与 build 失败原因。

# CryptoLab 项目进度评估报告

- 生成时间：2026-06-29 17:34:58 +08:00
- 基于 commit hash：`c57f053f8eeed532aa7df5a51b06210be004df40`
- 评估目录：`D:\Nnutural\Desktop\BUPT_6\SecureProgrammingTechnologyandCaseDevelopment\期中作业\CryptoLab`
- 证据归档：`docs/progress_evidence/`

> 说明：本机 shell 为 PowerShell。步骤一中用户给出的 `grep -rn` 命令，本次用 `rg -n` 执行等价扫描，并在附录记录实际命令、输出和退出码。`rg` 无命中时退出码为 1，不代表命令执行失败。

## 0. 执行摘要

当前工程状态为 **✅ 核心代码可验收，🟡 交付材料与容器构建仍需收口**。证据包括：`cargo test --manifest-path rust_core/Cargo.toml --no-fail-fast` 输出 `53 passed; 0 failed; 3 ignored`；`pytest --tb=no -q` 输出 `254 passed, 1 deselected`；`frontend npm run build` 成功，仅 Vite chunk size warning。静态扫描显示 `rust_core/src` 内 `todo!()`、`unimplemented!()`、`TODO|FIXME|XXX` 均无命中；但 `api_server/app/services/demo_service.py` 仍有 4 个 `NotImplementedError`，因此该历史占位文件必须标记为 ❌ 未完成，虽然当前 demo 路由实际调用的是 `demos_service.py`。

当前工作树不是干净状态：评估开始时 `git status --short` 显示 `README.md`、`cryptolab.db` 已修改，`.codegraph/daemon.pid` 已删除，且本次新增了 `docs/progress_evidence/` 与本报告。以下结论只基于本轮命令输出与文件内容，不把历史会话描述当作唯一证据。

## 1. 算法层完成度（rust_core/）

状态标准：✅ = 无 `todo!()`/`unimplemented!()` 且本轮 cargo test 通过；🟡 = 主要路径可用但有模式/边界/慢测限制；❌ = 仍有占位或无测试证据。

| 模块 | 子算法 | 实现状态 | 测试状态 | 测试向量来源 | 备注 |
|---|---|---:|---:|---|---|
| 编码 | Base64 | ✅ | ✅ cargo 全绿 | RFC 4648 / Python base64 | `encoding::base64` 测试在 cargo 输出中通过 |
| 编码 | UTF-8 | ✅ | ✅ cargo 全绿 | RFC 3629 / Python codec | `encoding::utf8::tests::encode_matches_rfc3629_widths` 通过 |
| 哈希 | SHA1 | ✅ | ✅ cargo 全绿 | FIPS 180-4 / hashlib | 含 million-a 与 streaming 测试 |
| 哈希 | SHA224/SHA256/SHA384/SHA512 | ✅ | ✅ cargo 全绿 | NIST/FIPS / hashlib | `sha256_nist_short_vectors`、1MB streaming 通过 |
| 哈希 | SHA3 / RIPEMD160 | ✅ | ✅ pytest 交叉验证覆盖 | NIST / hashlib | Rust 生产路径使用 crate 包装，符合文件实现事实 |
| 哈希 | HMAC-SHA1/HMAC-SHA256 | ✅ | ✅ cargo 全绿 | RFC 2202 / RFC 4231 | `subtle::ConstantTimeEq` 有 grep 证据 |
| 哈希 | PBKDF2-HMAC-SHA256 | ✅ | ✅ cargo 全绿 | RFC / cryptography | `pbkdf2_hmac_sha256_known_vectors` 通过 |
| 对称 | AES ECB/CBC/CTR/GCM | ✅ | ✅ cargo 全绿 | NIST SP 800-38A/38D | AES verbose trace 也通过 FIPS 197 中间状态测试 |
| 对称 | SM4 ECB/CBC | ✅ | ✅ cargo/pytest | GB/T 32907 / gmssl | `sm4.rs` 仅对不支持模式返回 unsupported，不是占位 |
| 对称 | RC6 ECB/CBC | 🟡 | ✅ cargo/pytest | RC6 paper vectors | 实现存在，但代码限制模式为 ECB/CBC，非全模式覆盖 |
| 公钥 | RSA-1024 keygen/encrypt/decrypt/sign/verify | ✅ | ✅ cargo/pytest | RFC 8017 / cryptography | 2 个 RSA 慢测被标记 ignored；普通测试全绿 |
| 公钥 | ECC-160 / ECDSA | ✅ | ✅ cargo/pytest | secp160r1 / RFC 6979 | ECDSA KAT-only 对照受主流库支持限制 |

算法层量化：按课程列出的 15 项算法（AES、SM4、RC6、SHA1、SHA256、SHA3、RIPEMD160、HMAC-SHA1、HMAC-SHA256、PBKDF2、Base64、UTF-8、RSA-1024、ECC-160、ECDSA）统计，**15/15 有实现与测试证据 = 100%**。其中 RC6 标为 🟡，原因是模式覆盖限制。

## 2. 接口层完成度（api_server/）

`api_server/app/main.py` 注册 11 个 router；脚本抽取到 32 个端点。`api_server/app/routers` 未命中 `NotImplementedError`，端点均导入 schema 与 service。`api_server/app/services/demo_service.py` 是未接入当前 router 的旧占位文件，仍需清理或补实。

| 模块 | 端点路径 | Handler 状态 | Schema 状态 | 测试状态 |
|---|---|---:|---:|---:|
| auth | `POST /api/v1/auth/register`、`login`、`logout`、`GET /me` | ✅ | ✅ | ✅ `test_auth.py`/`test_jwt.py` |
| symmetric | `POST /api/v1/symmetric/keygen` | ✅ | ✅ | ✅ `test_symmetric.py`/`test_keys.py` |
| symmetric | `POST /api/v1/symmetric/{algo}/encrypt`、`decrypt` | ✅ | ✅ | ✅ 含 AES verbose 专项 |
| hash | `POST /api/v1/hash/{algo}` | ✅ | ✅ | ✅ `test_hash.py` |
| hash | `POST /api/v1/hash/hmac/{algo}`、`pbkdf2` | ✅ | ✅ | ✅ `test_hash.py` |
| encoding | `POST /api/v1/encoding/base64/{op}` | ✅ | ✅ | ✅ `test_encoding.py` |
| encoding | `POST /api/v1/encoding/utf8/{op}` | ✅ | ✅ | ✅ `test_encoding.py`/cargo UTF-8 |
| pubkey | RSA keygen/encrypt/decrypt/sign/verify | ✅ | ✅ | ✅ `test_pubkey.py` |
| pubkey | ECC keygen、ECDSA sign/verify | ✅ | ✅ | ✅ `test_pubkey.py` |
| keys | list/export public/delete | ✅ | ✅ | ✅ `test_keys.py` |
| audit | `GET /api/v1/audit/logs` | ✅ | ✅ | ✅ `test_audit.py` |
| demos | 4 个漏洞 demo | ✅ | ✅ | ✅ `test_demos.py` |
| scenarios | secure file send/receive | ✅ | ✅ | ✅ `test_scenarios.py` |
| benchmark | `GET /api/v1/benchmark/{algo}` | ✅ | ✅ | ✅ `test_benchmark.py` |
| metrics | `GET /api/v1/metrics` | ✅ | ✅ | ✅ `test_metrics.py` |

接口量化：**32/32 router 端点有 handler = 100%**。但服务层旧文件 `demo_service.py` 存在 4 个 `NotImplementedError`，按核心原则计为 ❌ 待处理遗留。

## 3. 数据层完成度

Alembic 迁移脚本共 2 个：`0001_initial_schema.py` 创建 `users/key_store/operation_logs` 并加审计不可变触发器；`0002_fix_algorithm_metrics_schema.py` 创建/修正 `algorithm_metrics`。模型字段抽取如下：`User` 含 `id, username, password_hash, salt, role, last_login_at` 并继承 `created_at`；`KeyStore` 含设计方案要求字段并继承 `created_at`；`OperationLog` 含 `trace_id, user_id, operation, algorithm, key_id, input_hash, output_hash, status_code, duration_ms, client_ip, user_agent` 并继承 `created_at`；`AlgorithmMetric` 含 `algorithm, operation, data_size_bytes, duration_ns, memory_kb, recorded_at`。

逐表对比设计方案 §4.3：✅ 四张核心表均有模型与迁移；🟡 `users.id`、`operation_logs.id` 在模型中为 Integer/BigInteger 适配 SQLite，不是 PostgreSQL `BIGSERIAL` 字面类型；🟡 `operation_logs.client_ip` 用 `String(64)`，不是 PostgreSQL `INET` 字面类型，但本地 SQLite 可运行。Redis/缓存证据显示实际 key 模式为 `rate_limit:{ip}:{path_prefix}` 与 `jwt_blacklist:{jti}`，与设计方案 §4.4 一致。

本地 SQLite 只读查询显示：`users=8`、`key_store=11`、`operation_logs=16`、`algorithm_metrics=0`。因此“审计表有数据”✅，“当前本地 metrics 表有数据”❌。

## 4. 横切关注点

| 关注点 | 状态 | 证据 |
|---|---:|---|
| JWT 鉴权中间件 | ✅ | `middleware/auth.py`、`core/security.py` 命中 `jwt`、`Bearer`、黑名单 |
| 限流中间件 | ✅ | `rate_limit.py` 生成 `rate_limit:{ip}:{path_prefix}` 并走 cache |
| 审计日志写入 | ✅ | `audit_service.py` 构造 `OperationLog`；SQLite 有 16 行 |
| 统一状态码 | ✅ | `StatusCode` 共 28 项，被引用 211 次 |
| 常时间比较 | ✅ | Rust 命中 `subtle::ConstantTimeEq`；Python 命中 `hmac.compare_digest` |
| 密钥加密存储 | ✅ | `core/kek.py` HKDF-SHA256 派生 KEK，AES-256-GCM 包装 key material |
| Trace ID 贯穿 | ✅ | `context.py`、`TraceIDMiddleware`、异常响应、审计服务均命中 `trace_id` |

## 5. 前端完成度

`frontend/src/views` 有 12 个 `.tsx` view，`frontend/src/api` 有 12 个 API 模块；`frontend/src` 下没有 `.vue` 文件，因此“Vue 空模板”不存在。`npm test` ❌，原因是 `package.json` 没有 `test` 脚本；`npm run build` ✅，输出 `✓ built in 17.01s`，同时有 chunk size warning。

| 视图 | 状态 | 证据 |
|---|---:|---|
| Dashboard | ✅ | `Dashboard.tsx` + `metrics/audit/keys` API 模块 |
| SymmetricView | ✅ | `symmetric.ts`，AES verbose 组件存在 |
| HashView | ✅ | `hash.ts` |
| HmacPbkdf2View | ✅ | `hash.ts` |
| EncodingView | ✅ | `encoding.ts` |
| RsaView / EccView | ✅ | `pubkey.ts` |
| KeysView | ✅ | `keys.ts` |
| AuditView | ✅ | `audit.ts` |
| BenchmarkView | ✅ | `benchmark.ts` |
| DemosView | ✅ | `demos.ts` |
| ScenariosView | ✅ | `scenarios.ts` |

## 6. 部署 & DevOps

`docker compose -f deploy/docker-compose.yml config` ✅ 通过并输出 api、frontend、nginx、postgres、redis、rust-builder 等服务配置。`docker compose build` ❌ 未成功，原因是 Docker daemon 未运行：`open //./pipe/docker_engine: The system cannot find the file specified.` 三个 Dockerfile 检查：`Dockerfile.frontend` 是 multi-stage；`Dockerfile.rust` 是单阶段 one-shot builder；`Dockerfile.api` 不是传统 multi-stage，且包含 BuildKit mount 安装 wheel 的逻辑。`nginx.conf` ✅ 配置 HTTPS、HTTP 跳转、API 反代与 per-IP 限流。

## 7. 创新点 & 演示模块

| 特色 | 状态 | 实际产出 |
|---|---:|---|
| Rust + Python 双语异构 | ✅ | `.venv` 中可 `import cryptolab_core`，公开符号 49 个 |
| 三重验证体系 | ✅ | `test_cross_validation.py`、`docs/cross_validation_matrix.md`；本轮 pytest 全绿 |
| 中间过程可视化 | ✅ | `aes_encrypt_with_trace`、`AesTraceViewer.tsx`、`test_aes_verbose.py` |
| 漏洞攻击 Demo（4 个） | ✅ | `routers/demos.py` 4 端点调用 `demos_service.py` |
| 审计可观测性 | 🟡 | 写入逻辑与本地 operation_logs 数据存在；metrics 本地表当前 0 行 |

## 8. 文档完成度

`README.md` 当前已出现 React/FastAPI 描述，未命中旧 `Vue3/init/todo` 关键词；但工作树显示 README 已修改，是否最终版需由用户确认。`CLAUDE.md` 仍写 “Benchmark note: backend benchmark service currently supports SHA-256 only”，而实际 `benchmark_service.py` 已支持 AES/SM4/RC6/SHA/HMAC/PBKDF2/RSA/ECC/ECDSA 多分支，故 `CLAUDE.md` 需要更新。`docs/` 下已有 `README.md`、`verbose_mode.md`、`cross_validation_matrix.md`、AES verbose JSON/截图、本报告和证据目录。35 页 PDF 报告未在仓库中发现成品；仍缺最终排版、系统截图、接口调用截图、Docker build 证据与性能图表素材整理。

## 9. 整体进度量化

- 算法层完成度：**15/15 = 100%**；其中 RC6 因模式限制标 🟡。
- 接口端点完成度：**32/32 = 100%**；另有 1 个旧 service 文件含 4 个占位函数，标 ❌ 遗留。
- 测试覆盖：Rust **53 passed / 0 failed / 3 ignored**；API **254 passed / 0 failed / 1 deselected**；前端 `npm test` **0 项执行，脚本缺失**；前端 build 通过。
- 部署验证：compose config 通过；compose build 因 Docker daemon 未运行失败。
- 综合完成度：**88%**。扣分项来自 Docker build 未验证、前端无 test 脚本、旧占位 service 未清理、CLAUDE/报告材料未收口、本地 metrics 表无数据。
- 预估距离作业可提交：清理遗留与文档 2-4 小时，Docker/截图/报告素材 4-8 小时，最终 PDF 排版 6-10 小时。

## 10. 风险与下一步建议

1. 阻塞项：Docker daemon 未运行导致 `docker compose build` 没有真实构建证据；如果提交要求容器化演示，必须优先补跑。
2. 质量风险：`api_server/app/services/demo_service.py` 仍有 `NotImplementedError`，即使当前未接入 router，也会被人工 grep 认为未完成；建议删除或补实现并解释迁移到 `demos_service.py` 的原因。
3. 文档风险：`CLAUDE.md` benchmark 描述与实际代码冲突，最终报告/PDF 仍缺成品；`README.md` 当前已修改但需要复核并提交。
4. 报告素材缺口：需要 OpenAPI 截图、前端 12 视图截图、AES verbose 截图、接口调用响应、Docker build/up 输出、性能图或 metrics 数据。
5. 建议下一个会话目标：先清理 `demo_service.py` 占位和更新 `CLAUDE.md`，再在 Docker daemon 可用环境下补跑 `docker compose build` 与截图采集。

---

# 附录 A：静态扫描命令完整输出

## A.1 Git 基线

```text
PS> git rev-parse HEAD
c57f053f8eeed532aa7df5a51b06210be004df40

[exit=0]
```

```text
PS> git status --short
 D .codegraph/daemon.pid
 M README.md
 M cryptolab.db
?? docs/progress_evidence/

[exit=0]
```

## A.2 Rust 占位扫描

```text
PS> rg -n "todo!\(\)" rust_core/src

[exit=1]
```

```text
PS> rg -n "unimplemented!" rust_core/src

[exit=1]
```

```text
PS> rg -n "TODO|FIXME|XXX" rust_core/src

[exit=1]
```

## A.3 API 占位扫描

```text
PS> rg -n "NotImplementedError|raise NotImplemented" api_server/app
api_server/app\services\demo_service.py:18:    raise NotImplementedError(
api_server/app\services\demo_service.py:25:    raise NotImplementedError(
api_server/app\services\demo_service.py:31:    raise NotImplementedError(
api_server/app\services\demo_service.py:37:    raise NotImplementedError(

[exit=0]
```

```text
PS> rg -n "TODO|FIXME" api_server/app

[exit=1]
```

## A.4 前端占位与 Vue 文件扫描

```text
PS> rg -n "TODO|FIXME" frontend/src

[exit=1]
```

```text
PS> Get-ChildItem -Recurse -File frontend/src -Filter *.vue | Select-Object FullName,Length

[exit=0]
```

# 附录 B：测试与部署命令完整输出

## B.1 Rust 测试

```text
PS> cargo test --manifest-path rust_core/Cargo.toml --no-fail-fast 2>&1 | Select-Object -Last 50
test modes::gcm::tests::gf_mul_identity_cases ... ok
test modes::gcm::tests::ghash_empty_is_zero ... ok
test modes::tests::zero_unpad_is_rejected ... ok
test encoding::base64::tests::roundtrip_null_bytes_and_utf8 ... ok
test modes::tests::pkcs7_adds_full_block_on_boundary ... ok
test bigint::tests::mod_inverse_self_check ... ok
test encoding::utf8::tests::encode_matches_rfc3629_widths ... ok
test hash::sha1::tests::fips_180_4_classic_vectors ... ok
test hash::hmac::tests::rfc_2202_hmac_sha1_vectors ... ok
test pubkey::demos::tests::cube_root_exact_and_floor_cases ... ok
test modes::tests::ansi_x923_roundtrip_and_rejects_bad_bytes ... ok
test pubkey::ecc::tests::double_matches_add ... ok
test hash::sha2::tests::sha256_nist_short_vectors ... ok
test pubkey::ecc::tests::secp160r1_base_point_is_on_curve ... ok
test pubkey::rsa::tests::rsa_crt_decrypt_sign_stress_1000 ... ignored, RSA-1024 CRT stress test is intentionally slow
test pubkey::rsa::tests::rsa_keygen_oaep_pss_roundtrip ... ignored, RSA-1024 key generation is intentionally slow
test pubkey::rsa::tests::mgf1_is_deterministic ... ok
test pubkey::rsa::tests::private_from_parts_preserves_public_exponent_for_blinding ... ok
test pubkey::rsa::tests::crt_recombination_handles_m1_less_than_m2 ... ok
test pubkey::rsa::tests::rejects_low_public_exponent ... ok
test pubkey::rsa::tests::crt_recombination_reduces_m2_mod_p_before_subtracting ... ok
test symmetric::aes::tests::aes128_cbc_nist_sp_800_38a_f_2_1 ... ok
test pubkey::rsa::tests::blinded_decrypt_matches_plain ... ok
test symmetric::aes::trace::aes192_and_aes256_trace_shapes_match_key_size ... ok
test symmetric::aes::tests::aes128_gcm_nist_sp_800_38d_cases ... ok
test symmetric::aes::tests::aes128_ctr_nist_sp_800_38a_f_5_1 ... ok
test symmetric::aes::tests::aes128_ecb_nist_sp_800_38a_f_1_1 ... ok
test symmetric::aes::tests::aes192_and_aes256_ecb_vectors ... ok
test symmetric::rc6::tests::rc6_paper_appendix_b_zero_vector ... ok
test symmetric::aes::trace::fips_197_aes128_trace_matches_every_intermediate_state ... ok
test symmetric::sm4::tests::gb_t_32907_appendix_a_single_block ... ok
test pubkey::ecc::tests::group_law_for_small_scalars ... ok
test pubkey::demos::tests::ecdsa_recover_d_from_reused_k ... ok
test hash::sha1::tests::million_a_vector ... ok
test bigint::tests::miller_rabin_accepts_first_100_odd_primes ... ok
test hash::pbkdf2::tests::pbkdf2_hmac_sha256_known_vectors ... ok
test pubkey::ecc::tests::order_times_base_point_is_infinity ... ok
test hash::sha1::tests::streaming_matches_one_shot_for_random_1mb ... ok
test hash::sha2::tests::sha256_streaming_matches_one_shot_for_random_1mb ... ok
test pubkey::ecdsa::tests::tampering_fails ... ok
test pubkey::ecdsa::tests::sign_verify_roundtrip ... ok

test result: ok. 53 passed; 0 failed; 3 ignored; 0 measured; 0 filtered out; finished in 0.36s

   Doc-tests cryptolab_core

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

[exit=0]
```

## B.2 API 测试

```text
PS> Push-Location api_server; pytest --tb=no -q 2>&1 | Select-Object -Last 30; Pop-Location
........................................................................ [ 28%]
........................................................................ [ 56%]
........................................................................ [ 85%]
......................................                                   [100%]
254 passed, 1 deselected in 81.19s (0:01:21)

[exit=0]
```

## B.3 前端测试与构建

```text
PS> Push-Location frontend; npm test 2>&1 | Select-Object -Last 20; Pop-Location
npm error Missing script: "test"
npm error
npm error To see a list of scripts, run:
npm error   npm run
npm error A complete log of this run can be found in: D:\Nnutural\Desktop\BUPT_6\SecureProgrammingTechnologyandCaseDevelopment\期中作业\CryptoLab\.npm-cache\_logs\2026-06-29T09_31_15_327Z-debug-0.log

[exit=1]
```

```text
PS> Push-Location frontend; npm run build 2>&1 | Select-Object -Last 40; Pop-Location

> cryptolab-frontend@0.1.0 build
> tsc -b && vite build

vite v6.4.3 building for production...
transforming...
✓ 2354 modules transformed.
rendering chunks...
computing gzip size...
dist/index.html                   0.58 kB │ gzip:   0.41 kB
dist/assets/index-DW2n111Y.css   47.30 kB │ gzip:   8.76 kB
dist/assets/index-mewGIr9j.js   764.78 kB │ gzip: 231.34 kB

(!) Some chunks are larger than 500 kB after minification. Consider:
- Using dynamic import() to code-split the application
- Use build.rollupOptions.output.manualChunks to improve chunking
- Adjust chunk size limit for this warning via build.chunkSizeWarningLimit.
✓ built in 17.01s

[exit=0]
```

## B.4 Docker

```text
PS> docker compose -f deploy/docker-compose.yml config
name: deploy
services:
  api:
    build:
      context: D:\Nnutural\Desktop\BUPT_6\SecureProgrammingTechnologyandCaseDevelopment\期中作业\CryptoLab
      dockerfile: deploy/Dockerfile.api
    container_name: cryptolab-api
    depends_on:
      postgres:
        condition: service_healthy
        required: true
      redis:
        condition: service_healthy
        required: true
      rust-builder:
        condition: service_completed_successfully
        required: true
    environment:
      CRYPTOLAB_DATABASE_URL: postgresql+asyncpg://cryptolab:cryptolab@postgres:5432/cryptolab
      CRYPTOLAB_ENVIRONMENT: staging
      CRYPTOLAB_JWT_SECRET: dev-jwt-secret-change-me
      CRYPTOLAB_MASTER_KEY_HEX: "0000000000000000000000000000000000000000000000000000000000000000"
      CRYPTOLAB_REDIS_URL: redis://redis:6379/0
    ports:
      - mode: ingress
        target: 8000
        published: "8000"
        protocol: tcp
...
[exit=0]
```

```text
PS> docker compose -f deploy/docker-compose.yml build 2>&1 | Select-Object -Last 80
error during connect: this error may indicate that the docker daemon is not running: Head "http://%2F%2F.%2Fpipe%2Fdocker_engine/_ping": open //./pipe/docker_engine: The system cannot find the file specified.

[exit=1]
```

# 附录 C：关键计数与只读数据库查询

```text
status_codes=28
status_code_references=211
router_endpoints=32
frontend_views=12
frontend_api_modules=12
alembic_migrations=2
pytest_summary= 254 passed, 1 deselected in 81.19s (0:01:21)
cargo_summary= test result: ok. 53 passed; 0 failed; 3 ignored; 0 measured; 0 filtered out; finished in 0.36s
```

```text
PS> .\.venv\Scripts\python.exe - <<PY
import cryptolab_core
public = [x for x in dir(cryptolab_core) if not x.startswith('_')]
print(cryptolab_core.__name__)
print(len(public))
print(','.join(public[:20]))
PY
cryptolab_core
49
aes_decrypt,aes_encrypt,base64_decode,base64_encode,cryptolab_core,ecc_generate_keypair,ecc_keygen,ecdsa_demo_recover_d_from_k_reuse,ecdsa_demo_sign_with_k,ecdsa_sign,ecdsa_verify,hmac_sha1,hmac_sha256,pbkdf2_hmac_sha256,rc6_decrypt,rc6_encrypt,ripemd160,ripemd160_digest,rsa_decrypt,rsa_decrypt_oaep

[exit=0]
```

```text
PS> sqlite3 cryptolab.db .tables; select row counts
algorithm_metrics  key_store          operation_logs     users
table_name         rows
-----------------  ----
users              8
key_store          11
operation_logs     16
algorithm_metrics  0

[exit=0]
```

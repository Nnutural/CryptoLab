# AGENTS.md — CryptoLab Codex 工作指南

这份文档给 Codex CLI / Codex App 使用。它不是 `CLAUDE.md` 的翻译版：`CLAUDE.md` 负责短而硬的约束和状态快照，本文件负责把 CryptoLab 的工程意图、数据流、常见任务和调试方法讲清楚。

> 注意：OpenAI Codex 默认会沿当前工作目录向上查找 `AGENTS.md` / `AGENTS.override.md`。本项目把详尽中文指南放在 `.codex/AGENTS.md`，如果希望 Codex CLI 自动按“Codex home”方式加载它，可以在项目根目录用 `CODEX_HOME=$(pwd)/.codex codex ...`（PowerShell: `$env:CODEX_HOME=(Get-Location).Path + "\.codex"`）。在 Codex App 中，直接阅读本文件即可。

## 1. 项目全景：这不是一个“调库演示”

CryptoLab 是 BUPT 安全编程课程的期中作业。它的价值不只是把算法跑通，而是展示“手写密码算法如何被包装成一个接近生产形态的 Web 服务”。

项目分成两层：

- **底层 L2：Rust 手写算法库**  
  目录是 `rust_core/`。这里实现 AES、SM4、RC6、SHA、HMAC、PBKDF2、Base64、RSA、ECC、ECDSA 等原语，并通过 PyO3 暴露给 Python。算法模块应该像一个纯 Rust crate：不认识 HTTP、不认识 JSON、不认识数据库。

- **上层 L3-L6：服务与界面**  
  目录是 `api_server/` 和 `frontend/`。FastAPI 负责鉴权、限流、审计、密钥存储和请求/响应契约；React 负责 12 个教学视图。PostgreSQL/SQLite 和 Redis 分别承担持久化与缓存/黑名单/限流。

核心调用链如下：

```text
React View
  -> frontend/src/api/*.ts
  -> HTTP /api/v1/...
  -> api_server/app/routers/<module>.py
  -> api_server/app/schemas/<module>.py
  -> api_server/app/services/<module>_service.py
  -> import cryptolab_core
  -> rust_core/src/ffi.rs
  -> rust_core/src/<group>/<algo>.rs
```

理解这条链后，排查问题就简单很多：前端报错先看请求体；后端 422 看 Pydantic；后端 500 看 service 包装和 Rust panic；返回显示空白看 response 字段名。

## 2. 当前状态速览

### 2.1 最近关键变更

- 前端已经从旧 Vue3 设想完全切换到 **React 18 + Vite 6 + Tailwind 4 + Radix UI**。
- `frontend/src/views/` 下 12 个视图均已 React 化：Dashboard、Symmetric、Hash、HMAC/PBKDF2、Encoding、RSA、ECC、Keys、Audit、Benchmark、Demos、Scenarios。
- 前端 API 调用集中在 `frontend/src/api/*.ts`，页面不应直接裸调 `axios`。
- 后端已经具备 JWT 鉴权、用户系统、审计落库、Redis 限流、Trace ID、统一异常包装。
- 密钥材料通过 **HKDF-SHA256 KEK + AES-256-GCM 信封加密** 后落库。
- Rust 算法清单中的 UTF-8 encode/decode 已实现；`rg "todo!\\(|unimplemented!\\(" rust_core/src -g "*.rs"` 不应再命中算法缺口。

### 2.2 版本依赖

| 层 | 关键依赖 |
| --- | --- |
| Rust | Rust 1.75, PyO3 0.20, num-bigint 0.4, subtle 2.5, rand 0.8, zeroize 1.7 |
| API | FastAPI 0.110, Pydantic 2.6, SQLAlchemy 2.0, Alembic 1.13, Redis 5.0, PyJWT 2.8, structlog 24.1 |
| Frontend | React 18.3, Vite 6.3, TypeScript 5.7, Tailwind 4.1, Radix UI, axios 1.7 |

### 2.3 Rust 实现覆盖

| 组 | 当前状态 |
| --- | --- |
| 对称算法 | AES、SM4、RC6 已实现；模式含 ECB/CBC/CTR/GCM，其中 RC6 只支持 ECB/CBC |
| Hash/KDF | SHA1、SHA2、SHA3、RIPEMD-160、HMAC-SHA1/SHA256、PBKDF2-HMAC-SHA256 已实现 |
| 编码 | Base64 与 UTF-8 encode/decode 已实现 |
| 公钥 | RSA-1024 OAEP/PSS、ECC secp160r1、ECDSA 已实现 |
| 漏洞演示 | ECB 图像泄露、ECDSA k 复用、RSA e=3、PBKDF2 迭代影响已接入实际 demo service |
| 综合场景 | 安全文件传输 send/receive 已接入 RSA-OAEP + AES-GCM + ECDSA |

## 3. 快速上手：从 0 到本地跑起来

以下步骤是给“我要真的启动项目”的场景。文档修改任务不要启动服务。

### 3.1 每个新终端先加载隔离环境

```powershell
cd D:\Nnutural\Desktop\BUPT_6\SecureProgrammingTechnologyandCaseDevelopment\期中作业\CryptoLab
. .\scripts\env.ps1
```

加载后应当使用项目内目录：

```powershell
$env:CARGO_HOME
$env:RUSTUP_HOME
npm config get prefix --location project
```

设计意图：课程项目可能在不同机器上跑，依赖必须留在项目目录内，不能污染全局 Cargo、Python、npm。

### 3.2 首次安装依赖

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1
```

如果只需要局部安装：

```powershell
# Python API venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e api_server[dev]

# Rust -> Python extension
powershell -ExecutionPolicy Bypass -File .\scripts\build-rust.ps1

# Frontend
cd frontend
npm install
```

### 3.3 数据库迁移

```powershell
cd api_server
alembic upgrade head
```

后端配置读取 `api_server/app/core/config.py`。本地开发通常使用 `.env` 和项目内 SQLite/PostgreSQL，具体以当前仓库配置为准。

### 3.4 启动服务

不需要单独启动 Rust 后端。Rust 是 Python 扩展模块 `cryptolab_core`，由 FastAPI 进程导入。

```powershell
# terminal 1
. .\scripts\env.ps1
uvicorn app.main:app --reload --app-dir api_server

# terminal 2
. .\scripts\env.ps1
cd frontend
npm run dev
```

前端默认是 Vite 地址，通常为 `http://localhost:5173`。后端 OpenAPI 文档在 `http://localhost:8000/docs`（取决于配置是否开启 docs）。

## 4. 目录怎么读

### 4.1 `rust_core/`

重要文件：

- `src/ffi.rs`：Python 绑定入口。任何新算法要给 Python 调用，都要在这里加 `#[pyfunction]` 和 `m.add_function(...)`。
- `src/error.rs`：Rust 错误类型。生产代码不要把错误吞成 panic。
- `src/traits.rs`：对称算法、Hash、公钥算法的共性 trait。
- `src/modes/`：ECB/CBC/CTR/GCM，供 AES/SM4/RC6 复用。
- `src/pubkey/demos.rs`：漏洞演示专用的不安全函数，生产路径不要调用。

Rust 侧的理想形态：

```rust
pub fn encrypt_mode(
    &self,
    plaintext: &[u8],
    mode: &str,
    iv: Option<&[u8]>,
    aad: Option<&[u8]>,
    padding: &str,
) -> CryptoResult<Vec<u8>> {
    // parse parameters, call pure mode implementation, return Result
}
```

不要在算法模块里出现 HTTP status、Pydantic 字段名、数据库 ID 之类概念。

### 4.2 `api_server/`

后端按“路由 -> DTO -> 服务 -> Rust/DB”分层：

- `routers/` 只负责 HTTP path/method、依赖注入、返回 `APIResponse`。
- `schemas/` 是 Pydantic 请求/响应契约，前端字段必须对齐这里。
- `services/` 做业务编排：取密钥、解密材料、调用 Rust、审计需要的数据。
- `models/` 是 SQLAlchemy ORM，不应被路由直接调用。
- `middleware/` 中 TraceID、RateLimit、JWTAuth、Audit 会影响每个请求。

典型服务流程：

```python
async def encrypt(db, user, algo, req):
    if req.algorithm != algo:
        raise CryptoAPIException(...)
    key_bytes = key_service.fetch_and_decrypt(db, user, req.key_id, "symmetric")
    import cryptolab_core
    ciphertext = cryptolab_core.aes_encrypt(...)
    return SymmetricEncryptResponse(...)
```

### 4.3 `frontend/`

当前是 React，不再是 Vue。关键目录：

- `src/api/`：axios wrapper 和模块化 API 函数。
- `src/views/`：12 个页面视图。
- `src/components/shared/`：通用展示组件。
- `src/stores/`：认证状态等全局状态。

前端排查优先顺序：

1. 看 view 实际传给 API 函数的对象。
2. 看 `src/api/*.ts` 拼出来的 URL/method/body。
3. 看后端 router/schema。
4. 看 view 读取 `resp.data.xxx` 的字段名。

## 5. API 契约全表

所有路径默认带 `/api/v1` 前缀。

### 5.1 认证与总览

| 模块 | Method | Path | 请求字段 | 响应字段 |
| --- | --- | --- | --- | --- |
| Auth | POST | `/auth/register` | `username,password` | `user_id,created_at` |
| Auth | POST | `/auth/login` | `username,password` | `access_token,token_type,expires_in` |
| Auth | POST | `/auth/logout` | header JWT | `null` |
| Auth | GET | `/auth/me` | header JWT | `user_id,username,roles` |
| Dashboard/Keys | GET | `/keys` | query none | `id,key_type,algorithm,paired_key_id,label,created_at,expires_at` |
| Dashboard/Audit | GET | `/audit/logs` | `user_id?,algorithm?,since?,until?,limit?,offset?` | `id,trace_id,operation,status_code,duration_ms,...` |

### 5.2 对称加密

| Method | Path | 请求字段 | 响应字段 | Rust |
| --- | --- | --- | --- | --- |
| POST | `/symmetric/keygen` | `algorithm,key_size(bytes),label?` | `key_id` | Python `secrets.token_bytes` + key store |
| POST | `/symmetric/{algo}/encrypt` | `algorithm,mode,padding,key_id,plaintext_b64,iv_hex?,aad_b64?` | `ciphertext_b64,algorithm,mode,duration_ms` | `aes_encrypt/sm4_encrypt/rc6_encrypt` |
| POST | `/symmetric/{algo}/decrypt` | `algorithm,mode,padding,key_id,ciphertext_b64,iv_hex?,aad_b64?` | `plaintext_b64,algorithm,mode,duration_ms` | `aes_decrypt/sm4_decrypt/rc6_decrypt` |

注意：

- `key_size` 是字节，不是 bit。AES 合法值 `16/24/32`，SM4/RC6 合法值 `16`。
- GCM IV 是 12 字节；CBC/CTR IV 是 16 字节。
- `padding` 后端枚举是 `PKCS7 | Zero | X923 | None`，不是 `ZeroPadding`。
- RC6 当前只支持 ECB/CBC。
- Verbose mode 仅支持 AES + ECB + 单个 16 字节明文分组；trace 含明文等价中间态，不进入 audit log 或 metrics。

### 5.2.1 特色三：Verbose Mode 数据流

AES verbose 是教学演示路径，不是普通加密路径的增强开关。数据流如下：

```text
rust_core/src/symmetric/aes.rs
  AesTrace / AesRoundTrace / AesTimings
  encrypt_block_with_trace()
  -> captures state after SubBytes, ShiftRows, MixColumns, AddRoundKey
  -> keeps normal encrypt_block() unchanged

rust_core/src/ffi.rs
  aes_encrypt_with_trace()
  -> validates plaintext.len() == 16
  -> returns (ciphertext_bytes, json.loads(serde_json(trace)))

api_server/app/schemas/symmetric.py
  SymmetricEncryptRequest.verbose
  AesTrace / AesRoundTrace response schema

api_server/app/routers/symmetric.py
  verbose=True
  -> require algorithm == aes
  -> require mode == ECB
  -> require decoded plaintext length == 16

api_server/app/services/symmetric_service.py
  aes_encrypt_with_trace_op()
  -> fetches user key
  -> calls cryptolab_core.aes_encrypt_with_trace
  -> intentionally skips metrics_service.record_nowait()

frontend/src/views/SymmetricView.tsx
  AES + ECB + encrypt
  -> 教学模式 toggle
  -> renders frontend/src/components/shared/AesTraceViewer.tsx
```

### 5.3 Hash / HMAC / PBKDF2

| Method | Path | 请求字段 | 响应字段 | Rust |
| --- | --- | --- | --- | --- |
| POST | `/hash/{algo}` | `data` | `digest_hex,algorithm` | `sha1/sha256/sha3_256/ripemd160/...` |
| POST | `/hash/hmac/{algo}` | `key,message,algorithm` | `mac_hex,algorithm` | `hmac_sha1/hmac_sha256` |
| POST | `/hash/pbkdf2` | `password,salt,iterations,key_len` | `derived_key_hex,algorithm,iterations,key_len,salt_hex` | `pbkdf2_hmac_sha256` |

### 5.4 编码

| Method | Path | 请求字段 | 响应字段 | 状态 |
| --- | --- | --- | --- | --- |
| POST | `/encoding/base64/encode` | `data` | `encoded` | 已实现 |
| POST | `/encoding/base64/decode` | `encoded` | `data`（原始 bytes 再 Base64 包装） | 已实现 |
| POST | `/encoding/utf8/encode` | `data` | `encoded`（UTF-8 bytes 再 Base64 包装） | 已实现 |
| POST | `/encoding/utf8/decode` | `data` 或 `encoded` | `data` | 已实现 |

### 5.5 RSA / ECC / ECDSA

| Method | Path | 请求字段 | 响应字段 | Rust |
| --- | --- | --- | --- | --- |
| POST | `/pubkey/rsa/keygen` | `bits=1024,e=65537,label?` | `private_key_id,public_key_id,algorithm,bits` | `rsa_generate_keypair` |
| POST | `/pubkey/rsa/encrypt` | `plaintext,key_id(public)` | `ciphertext_hex` | `rsa_encrypt_oaep` |
| POST | `/pubkey/rsa/decrypt` | `ciphertext_hex,key_id(private)` | `plaintext` | `rsa_decrypt_oaep` |
| POST | `/pubkey/rsa/sign` | `message,key_id(private)` | `signature_hex` | `rsa_sign_pss` |
| POST | `/pubkey/rsa/verify` | `message,signature_hex,key_id(public)` | `valid` | `rsa_verify_pss` |
| POST | `/pubkey/ecc/keygen` | `curve=secp160r1,label?` | `private_key_id,public_key_id,algorithm,curve` | `ecc_generate_keypair` |
| POST | `/pubkey/ecdsa/sign` | `message,key_id(private),curve` | `r_hex,s_hex,curve` | `ecdsa_sign` |
| POST | `/pubkey/ecdsa/verify` | `message,r_hex,s_hex,key_id(public),curve` | `valid,curve` | `ecdsa_verify` |

公钥材料读取：

| Method | Path | 响应字段 |
| --- | --- | --- |
| GET | `/keys/{public_key_id}/public` | `key_id,algorithm,material` |

`material` 对 RSA 通常是 `n_hex,e_hex`；对 ECC 通常是 `qx_hex,qy_hex,curve`。

### 5.6 Demo

| Method | Path | 请求字段 | 响应字段 |
| --- | --- | --- | --- |
| POST | `/demos/ecb_image_leak` | `image_b64,key_hex` | `original_png_b64,ecb_encrypted_png_b64,cbc_encrypted_png_b64,block_count,duplicate_block_ratio` |
| POST | `/demos/ecdsa_k_reuse` | `message1,message2,curve` | `private_key_hex,public_key,reused_k_hex,signature1,signature2,r_equal,recovered_d_hex` |
| POST | `/demos/rsa_low_exponent` | `message,bits=1024` | `n_hex,e,ciphertext_hex,message_bits,n_bits,cube_safe,recovered_plaintext` |
| POST | `/demos/pbkdf2_iteration_impact` | `password,salt_hex,key_len,iterations_list` | `measurements,ratio_1m_over_100k,verdict` |

### 5.7 综合场景与基准测试

| Method | Path | 请求字段 | 响应字段 |
| --- | --- | --- | --- |
| POST | `/scenarios/secure_file_transfer/send` | `file_b64,receiver_rsa_public_key_id|receiver_rsa_public_pem,sender_ecdsa_private_key_id|sender_ecdsa_private_hex,sender_ecdsa_curve` | `envelope,sender_summary` |
| POST | `/scenarios/secure_file_transfer/receive` | `envelope,receiver_rsa_private_key_id|receiver_rsa_private,sender_ecdsa_public_key_id|sender_ecdsa_public` | `plaintext_b64,verification,duration_ms` |
| GET | `/benchmark/{algo}` | path `algo` | `algorithm,data_size_bytes,iterations,total_ms,throughput_mb_per_s,ns_per_op` |

`benchmark_service.py` 当前只支持 `sha256` / `sha-256`，其它前端按钮应预期收到 unsupported。

## 6. 算法实现路线图

按课程设计方案的合理顺序看：

1. **编码基础**  
   Base64 与 UTF-8 已实现；后续编码类任务应优先补边界测试与前端展示一致性。

2. **摘要与 KDF**  
   SHA1/SHA2/SHA3/RIPEMD/HMAC/PBKDF2 已实现并通过 FFI 暴露。这里适合补充测试向量和性能基准。

3. **对称密码与模式**  
   AES/SM4/RC6 及 ECB/CBC/CTR/GCM 已接入。排错时优先看 key length、IV length、padding 字符串。

4. **公钥密码**  
   RSA/ECC/ECDSA 已接入 key store。前端和后端都必须区分 public/private key ID。

5. **教学 demo**  
   demo 可以使用不安全参数，但必须保持 warning、access dependency 和清晰命名，避免被生产路径误用。

6. **综合协议**  
   secure-file-transfer 是系统集成验证点：RSA 包会话密钥，AES-GCM 加密文件，SHA-256 摘要，ECDSA 签名。

## 7. 常见任务：一步步做

### 7.1 新增一个对称密码算法

假设要新增 `foo`：

1. **Rust 算法模块**  
   新建 `rust_core/src/symmetric/foo.rs`，实现纯 Rust API。优先复用 `modes/`。

2. **模块导出**  
   在 `rust_core/src/symmetric/mod.rs` 加：

   ```rust
   pub mod foo;
   ```

3. **FFI 绑定**  
   在 `rust_core/src/ffi.rs` 增加 `foo_encrypt` / `foo_decrypt` 的 `#[pyfunction]`，并在 pymodule 中 `m.add_function(...)`。

4. **后端 schema**  
   更新 `api_server/app/schemas/symmetric.py` 的 `AlgorithmName` 枚举，确认 key size、mode、padding 规则。

5. **后端 service**  
   在 `api_server/app/services/symmetric_service.py` 的函数映射里加入 `cryptolab_core.foo_encrypt/decrypt`。

6. **前端 API 与视图**  
   `frontend/src/api/symmetric.ts` 通常无需新增函数；在 `SymmetricView.tsx` 加算法选项、key size 选项和 mode 限制。

7. **验证顺序**  
   先 `cargo test --manifest-path rust_core/Cargo.toml foo`，再 `pytest api_server/tests`，最后 `cd frontend; npx tsc --noEmit`。

### 7.2 新增一个 React 视图页面

1. 在 `frontend/src/views/` 新建 `XxxView.tsx`。
2. 在 `frontend/src/api/` 新建或扩展模块 API 函数。
3. 在导航配置里注册 route/title/breadcrumb。
4. 页面里只调用 `src/api` 函数，不直接 `axios.post(...)`。
5. 根据后端 `APIResponse<T>` 读取 `resp.code/resp.message/resp.data`。
6. 失败展示优先使用 `err?.response?.data?.message || err?.message`。
7. 完成后跑 `cd frontend; npx tsc --noEmit`。

一个典型 API 函数：

```ts
import client, { type APIResponse } from "./client";

export async function runSomething(body: SomeRequest): Promise<APIResponse<SomeResponse>> {
  return client.post("/module/path", body);
}
```

### 7.3 调试前后端字段不匹配

按这个顺序，不要猜：

1. `frontend/src/views/XxxView.tsx`：实际传入什么对象？
2. `frontend/src/api/xxx.ts`：URL、method、body 是否又变形？
3. `api_server/app/routers/xxx.py`：path/method 是否存在？
4. `api_server/app/schemas/xxx.py`：字段名、类型、可选性、枚举是什么？
5. `api_server/app/services/xxx_service.py`：有没有手动 `validate_*()` 抛裸异常？
6. `rust_core/src/ffi.rs`：Python 函数名和参数顺序是什么？
7. `rust_core/src/<group>/<algo>.rs`：函数体是不是 `todo!()`、是否 panic？

经验规则：

- 422 多半是 Pydantic 字段/类型/枚举不对。
- 500 多半是 service 层裸异常、Rust panic、数据库/KEK 环境问题。
- 前端显示空白但网络 200，多半是 response 字段读取错。

### 7.4 调试 Rust panic / PyO3 错误

1. 先在 Rust 侧直接跑目标模块测试：

   ```powershell
   cargo test --manifest-path rust_core/Cargo.toml <module_name> -- --nocapture
   ```

2. 如果 Rust 侧通过，再重建 Python 扩展：

   ```powershell
   powershell -ExecutionPolicy Bypass -File .\scripts\build-rust.ps1
   ```

3. 用 Python 最小脚本直接 import：

   ```powershell
   .\.venv\Scripts\python.exe - <<'PY'
   import cryptolab_core
   print(cryptolab_core.sha256_digest(b"abc").hex())
   PY
   ```

4. 如果 API 仍 500，看 `api_server/app/services/*` 是否把 Rust `ValueError` 包装成 `CryptoAPIException`。

5. 如果 panic 只在 FastAPI 里出现，检查请求字段是否已经按 Base64/hex 转成 bytes。

### 7.5 看审计日志定位问题

审计中间件只记录摘要和元数据，不存原文。排查时看：

- `trace_id`：把前端错误、后端日志和审计记录串起来。
- `operation`：通常是 HTTP path 或服务操作。
- `algorithm`：算法维度。
- `status_code`：业务状态码，不等同于 HTTP status。
- `duration_ms`：定位 Rust 算法慢还是 DB/中间件慢。
- `input_hash/output_hash`：用于确认同一输入，不用于还原原文。

API 查询：

```powershell
# 需要带 Authorization header；这里只示意 query
GET /api/v1/audit/logs?algorithm=AES&since=2026-06-08T00:00:00&until=2026-06-08T23:59:59&limit=50
```

### 7.6 修复密钥相关问题

当前 key store 返回：

```json
{
  "id": "...",
  "key_type": "public | private | symmetric",
  "algorithm": "rsa | ecc | aes | sm4 | rc6",
  "paired_key_id": "...",
  "label": "...",
  "created_at": "...",
  "expires_at": null
}
```

注意：

- RSA encrypt / verify 用 public key ID。
- RSA decrypt / sign 用 private key ID。
- ECDSA sign 用 private key ID。
- ECDSA verify 用 public key ID。
- `GET /keys/{id}/public` 只接受 public 类型 key；如果手上是 private key，要先用 `paired_key_id` 找到 public key。

## 8. 安全设计背后的意图

### 8.1 为什么密钥要 KEK 包装

课程项目也应展示正确边界：数据库不可信时，密钥材料不能明文落库。`key_service.py` 会把 key material 序列化后用 KEK 派生出的 AES-256-GCM 信封加密。这样即使 `key_store` 泄漏，也不能直接拿到可用私钥或对称密钥。

### 8.2 为什么审计日志不存原文

审计要能定位问题，但不能变成新的敏感数据泄漏源。所以只存 SHA-256 指纹、状态、耗时、IP、trace ID。需要复现时用 trace ID 找请求，不从审计表还原明文。

### 8.3 为什么 demo 可以不安全

demo 的目的就是展示 ECB、ECDSA k 复用、RSA e=3、低 PBKDF2 迭代的风险。因此 demo 可以使用不安全参数，但必须隔离在 `/demos/*`，并保留 warning 和 access dependency。不要把 demo helper 接入生产加密/签名路径。

## 9. 协作风格建议

给 Codex 的工作方式：

- 先读契约，再改代码。CryptoLab 的多数 bug 不是算法错，而是字段名、编码方式、公私钥 ID 用错。
- 遇到前后端冲突时，优先适配前端；后端 DTO 是当前稳定契约，除非用户明确要求改后端。
- 修改 Rust 前先找测试向量；没有向量时先补最小 roundtrip，再补标准向量。
- 修改 API 前先画出 `View -> api.ts -> router -> schema -> service -> ffi` 的实际链路。
- 做 UI 时保持现有 React/Tailwind/Radix 风格，不把算法实验页改成营销页。

## 10. 少量必要红线

1. 不要把密钥、口令、JWT、私钥材料写进日志或审计表。
2. 不要在生产路径引入 raw RSA、随机 ECDSA k、ECB 默认模式等不安全行为。
3. 不要让 router 直接操作 ORM；走 service。
4. 不要在 React view 里绕过 `frontend/src/api` 裸调后端。
5. 不要凭字段名惯例猜契约；必须读 `schemas/` 和 `services/`。

## 11. 静态自检清单

做完任何改动后，根据改动范围选择：

```powershell
# Rust
cargo test --manifest-path rust_core/Cargo.toml
cargo clippy --manifest-path rust_core/Cargo.toml -- -D warnings

# API
pytest api_server/tests
ruff check api_server
mypy api_server/app

# Frontend
cd frontend
npx tsc --noEmit
npm run build
```

如果任务明确要求“不启动服务”，不要运行 `npm run dev`、`uvicorn`、`docker compose up`。

## 12. 当前最值得后续补的地方

- 扩展 `api_server/app/services/benchmark_service.py`，让前端 Benchmark 页面里的 AES/SM4/RC6/RSA/ECDSA 等按钮对应真实后端能力。
- 为关键 API 契约补集成测试，尤其是 symmetric Base64、RSA/ECC 公私钥 ID、secure-file-transfer。
- 对 demo endpoint 保持教学 warning，但可以补更明确的错误信息和输入示例。

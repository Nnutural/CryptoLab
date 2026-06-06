# CLAUDE.md — CryptoLab

> 给未来 Claude Code 会话的项目说明书。新会话进入本仓库后**先读本文件**，再读相关源码。

---

## 1. 项目是什么

CryptoLab 是 BUPT 信息安全专业 / 安全编程课程的期中作业。目标：实现 **15 种密码算法**（AES、SM4、RC6、SHA1/2/3、RIPEMD-160、HMAC、PBKDF2、Base64、UTF-8、RSA-1024、ECC-160、ECDSA），并把它们装进一个**生产级 Web 服务**里。

**双层架构**：

- **底层（L2）**：Rust 手写算法 + PyO3 暴露给 Python。位于 `rust_core/`。
- **上层（L3–L6）**：Python FastAPI 服务 + Vue3 前端 + PostgreSQL + Redis + Nginx + Docker。位于 `api_server/`、`frontend/`、`deploy/`。

完整设计：`../系统设计方案.md`（与本仓库同级目录的设计方案文档）。

---

## 2. 目录结构

```
CryptoLab/
├── rust_core/                    # L2: Rust 核心算法库
│   ├── Cargo.toml                # 依赖：pyo3, num-bigint, subtle, rand, sha2, sha3 (后两者仅用于对照测试)
│   ├── pyproject.toml            # maturin 配置
│   └── src/
│       ├── lib.rs                # crate 根 + PyO3 #[pymodule]
│       ├── ffi.rs                # Python 绑定层（所有 #[pyfunction] 集中在这）
│       ├── error.rs              # CryptoError 类型 + 与 PyErr 的转换
│       ├── traits.rs             # SymmetricCipher / HashAlgorithm / PublicKeyAlgorithm
│       ├── symmetric/            # aes.rs, sm4.rs, rc6.rs
│       ├── hash/                 # sha1.rs, sha2.rs, sha3.rs, ripemd.rs, hmac.rs, pbkdf2.rs
│       ├── encoding/             # base64.rs, utf8.rs
│       ├── pubkey/               # rsa.rs, ecc.rs, ecdsa.rs
│       ├── modes/                # ecb.rs, cbc.rs, ctr.rs, gcm.rs
│       └── bigint/               # mod.rs: 密码学专用大数
│
├── api_server/                   # L3 + L4: FastAPI 服务端
│   ├── pyproject.toml
│   ├── app/
│   │   ├── main.py               # FastAPI 入口，注册路由 + 中间件
│   │   ├── core/                 # config / exceptions / status_codes / security
│   │   ├── middleware/           # auth / rate_limit / audit / trace
│   │   ├── routers/              # 按算法类别拆分的 REST 路由
│   │   ├── services/             # 业务编排（不直接碰 ORM 的同级路由）
│   │   ├── models/               # SQLAlchemy ORM（users / key_store / operation_logs / algorithm_metrics）
│   │   ├── schemas/              # Pydantic DTO
│   │   └── db/                   # session / base / engine
│   ├── alembic/                  # 迁移
│   └── tests/                    # pytest，按 router 分文件
│
├── frontend/                     # L6: Vue3 + Vite + Element Plus
│   ├── package.json
│   ├── .npmrc                    # 强制本地 cache & prefix
│   ├── vite.config.ts
│   └── src/
│       ├── main.ts
│       ├── App.vue
│       ├── router/
│       ├── api/                  # axios 封装
│       └── views/                # 各算法演示页（symmetric / hash / encoding / pubkey / demos）
│
├── deploy/                       # L5 + 部署
│   ├── docker-compose.yml
│   ├── Dockerfile.api
│   ├── Dockerfile.rust
│   ├── Dockerfile.frontend
│   └── nginx.conf
│
├── scripts/                      # 一键化脚本（.sh 与 .ps1 等价并列）
│   ├── env.sh / env.ps1          # 设置项目级环境变量（CARGO_HOME 等）
│   ├── setup.sh / setup.ps1      # 首次环境初始化
│   ├── build-rust.sh / build-rust.ps1   # 编译 Rust → Python 扩展（maturin develop）
│   ├── test-all.sh / test-all.ps1
│   └── bench.sh / bench.ps1
│
├── benchmarks/                   # criterion 基准（占位）
├── docs/                         # 设计文档与报告（占位）
├── .cargo/config.toml            # Rust 工程级配置
├── .claude/                      # Claude Code 项目设置 + slash command
├── .gitignore
├── .editorconfig
├── README.md
├── CLAUDE.md                     # ← 你正在读
└── LICENSE                       # MIT
```

---

## 3. 构建与运行命令速查

Bash 与 PowerShell 等价，二选一。Windows 用户也可以直接在 Git Bash 里跑 Bash 列。

| 任务                    | Bash                                                            | PowerShell                                                                          |
| ----------------------- | --------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| **首次环境初始化**      | `source scripts/env.sh && bash scripts/setup.sh`                | `. .\scripts\env.ps1; powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1` |
| 每个新终端先做这一步    | `source scripts/env.sh`                                         | `. .\scripts\env.ps1`                                                               |
| 编译 Rust → Python 扩展 | `bash scripts/build-rust.sh`                                    | `powershell -ExecutionPolicy Bypass -File .\scripts\build-rust.ps1`                 |
| 单独 cargo build        | `cargo build --release --manifest-path rust_core/Cargo.toml`    | 同左                                                                                |
| Rust 测试               | `cargo test --manifest-path rust_core/Cargo.toml`               | 同左                                                                                |
| Rust lint               | `cargo clippy --manifest-path rust_core/Cargo.toml -- -D warnings` | 同左                                                                            |
| Rust 格式化             | `cargo fmt --manifest-path rust_core/Cargo.toml --all`          | 同左                                                                                |
| 启动 API（开发）        | `uvicorn app.main:app --reload --app-dir api_server`            | `uvicorn app.main:app --reload --app-dir api_server`                                |
| Python 测试             | `pytest api_server/tests`                                       | `pytest api_server/tests`                                                           |
| Python lint             | `ruff check api_server && mypy api_server/app`                  | `ruff check api_server; mypy api_server/app`                                        |
| Python 格式化           | `ruff format api_server`                                        | `ruff format api_server`                                                            |
| 启动前端 dev            | `cd frontend && npm run dev`                                    | `cd frontend; npm run dev`                                                          |
| 全栈跑测试              | `bash scripts/test-all.sh`                                      | `powershell -ExecutionPolicy Bypass -File .\scripts\test-all.ps1`                   |
| 基准测试                | `bash scripts/bench.sh`                                         | `powershell -ExecutionPolicy Bypass -File .\scripts\bench.ps1`                      |
| 容器化启动              | `docker compose -f deploy/docker-compose.yml up -d`             | `docker compose -f deploy/docker-compose.yml up -d`                                 |
| 数据库迁移              | `cd api_server && alembic upgrade head`                         | `cd api_server; alembic upgrade head`                                               |

---

## 4. 关键约束：依赖隔离（重要）

**所有依赖必须装在项目路径下**，禁止污染 `~/.cargo`、`~/.rustup`、全局 Python site-packages、全局 npm。

### 实现方式

| 工具链  | 项目内目录                | 触发机制                                      |
| ------- | ------------------------- | --------------------------------------------- |
| Rust    | `./.cargo-home`           | `scripts/env.sh` 设 `CARGO_HOME`              |
| rustup  | `./.rustup-home`          | `scripts/env.sh` 设 `RUSTUP_HOME`             |
| Python  | `./.venv`                 | `python -m venv .venv` + 后续始终在 venv 内   |
| npm     | `./.npm-cache`、`./.npm-global` | `frontend/.npmrc` 内 `cache=` / `prefix=`     |

### 检查方式

```bash
# 应当全部指向项目内路径
echo $CARGO_HOME       # 期望 .../CryptoLab/.cargo-home
echo $RUSTUP_HOME      # 期望 .../CryptoLab/.rustup-home
which python           # 期望 .../CryptoLab/.venv/bin/python
npm config get prefix  # 期望 .../CryptoLab/.npm-global
```

如果哪一项不对，**先 `source scripts/env.sh` 重新设环境，再继续**。**不要绕过**这条规则去用全局工具链。

---

## 5. 代码规范

### Rust

- 必须 `cargo fmt --all` 才能提交（CI 强制）
- 必须 `cargo clippy --all-targets -- -D warnings` 通过
- 公开 API（FFI、trait 默认实现、pub fn）必须有 `///` 文档注释，说明算法依据（NIST / RFC / GB/T）
- **生产路径禁止 `unwrap()` / `expect()`**。错误统一走 `CryptoError`（见 `rust_core/src/error.rs`）。仅允许在测试代码与确实 infallible 的常量初始化处使用
- 单元测试与生产代码同文件下方 `#[cfg(test)]` 模块，向量级测试统一放在每个算法子模块的尾部

### Python

- `ruff check` + `ruff format` + `mypy --strict app/`
- 公开模块的类型注解必须完整（含返回类型）
- 路由函数禁止直接调用 `models/` 里的 ORM 操作，必须经过对应 `services/`
- 异常统一抛 `app.core.exceptions.CryptoAPIException`，由全局 handler 转 `APIResponse`
- 日志输出统一用 `app.core.logging.get_logger(__name__)`，禁用裸 `print`

### TypeScript / Vue

- ESLint + Prettier 默认配置
- 组件用 `<script setup lang="ts">` 风格
- API 请求统一走 `src/api/`，禁止在组件里裸调 `axios`

---

## 6. 模块边界规则（架构红线）

| 红线                                                              | 违反后果                                  |
| ----------------------------------------------------------------- | ----------------------------------------- |
| **算法层（Rust）不感知 HTTP**。`symmetric/aes.rs` 里禁止出现任何 HTTP / JSON / FastAPI 概念 | 测试不可复用，把工程降级回"调库交差"      |
| **PyO3 绑定只放在 `rust_core/src/ffi.rs`**。算法子模块只暴露纯 Rust API | 算法模块无法独立给 criterion 基准复用     |
| **路由层（`routers/`）不直接 import `models/`**。所有数据库操作走 `services/` | 业务逻辑与持久层耦合，测试夹具难以铺设    |
| **`services/` 不直接构造 HTTP 异常**。统一抛 `CryptoAPIException` | 中间件无法统一包装响应                    |
| **审计日志不存原文**。`operation_logs` 只能存输入/输出的 SHA-256 指纹 | 出现密文落库 → 设计原则违反（隐私 + 合规） |

---

## 7. 安全红线

1. **生产路径禁用 `unwrap()` / `expect()`**：所有 `Result` 必须显式处理或 `?` 上抛。仅常量初始化与确认 infallible 的桩可豁免。
2. **敏感比较使用常时间函数**：MAC / 标签 / 哈希比较禁止使用 `==`，必须用 `subtle::ConstantTimeEq`（Rust）或 `hmac.compare_digest`（Python）。
3. **密钥与口令禁止进日志**：日志记录前必须经 `core.security.redact_sensitive()`。`Debug` 实现里包含密钥字段必须手写脱敏。
4. **随机数只用 OS CSPRNG**：Rust 用 `rand::rngs::OsRng`，Python 用 `secrets`。`rand::thread_rng()` 在生产路径禁用。
5. **私钥落库前必须用 KEK 加密**：明文私钥永不出 `services/key_service.py` 的范围。
6. **JWT 必须设过期 + 黑名单**：登出后 jti 写 Redis 黑名单直至原过期时间。
7. **ECDSA k 强制 RFC 6979 确定性派生**：禁止任何形式的随机 k 实现。
8. **RSA e 强制 ≥ 65537 + OAEP/PSS 填充**：不允许暴露 e=3 / 无填充接口（demo 演示路径除外，且必须前置 banner 提示）。
9. **SQL 全部走 SQLAlchemy ORM 参数化**：禁止字符串拼接 SQL。
10. **CORS 白名单显式列举**：禁止 `allow_origins=["*"]` 出现在生产 config。

---

## 8. 给新会话 Claude 的提示

### 进入新会话先读这些

1. 本文件 `CLAUDE.md`
2. `../系统设计方案.md`（与项目同级的完整设计）
3. 即将动的子目录的 `Cargo.toml` / `pyproject.toml` / 入口文件（`lib.rs` / `main.py`）

### 改动算法前必跑这些

```bash
# 1. 确认环境隔离
source scripts/env.sh

# 2. 跑当前模块测试基线
cargo test --manifest-path rust_core/Cargo.toml <algo_module>::

# 3. 改完后跑整套测试 + lint
bash scripts/test-all.sh
cargo clippy --manifest-path rust_core/Cargo.toml -- -D warnings
ruff check api_server
```

### 算法实现顺序建议（参考设计方案第十部分）

`Base64 / UTF-8` → `SHA1/2/3 + HMAC + PBKDF2` → `AES（含 GCM）+ SM4 + RC6` → `RSA + ECC + ECDSA` → `漏洞 Demo + 综合场景` → `前端 + 测试`。

### 写新算法时不要忘记

- 在 `rust_core/src/<group>/mod.rs` 里 `pub mod xxx;`
- 在 `rust_core/src/ffi.rs` 里 `m.add_function(wrap_pyfunction!(xxx, m)?)?;`
- 在 `api_server/app/routers/` 对应 router 接通到 `core` 模块
- 在 `api_server/app/services/` 写编排逻辑（审计、限流、密钥取出）
- 在 `api_server/tests/` 加测试，至少含 1 个 RFC/NIST 向量
- 在 `frontend/src/views/` 加一个最小演示页

---

## 9. 项目状态（init 完成时）

- 目录与依赖声明全部就位，`cargo check` / `pip install -e .` / `npm install` 应当成功
- 所有算法函数体为 `todo!()` 或 `raise NotImplementedError`
- 数据库迁移、Docker Compose 就绪，但**未启动**任何容器
- 没有写入用户全局目录的副作用

下一步：按设计方案第十部分顺序开始填实现。

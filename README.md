# CryptoLab

> 基于 **Rust + Python** 的密码算法实验平台
> 覆盖对称加密 / 哈希 / 编码 / 公钥密码四大类共 15 种算法
> 工程化、可审计、可扩展 — 不是「调库交差」，是「手写 + 服务化」

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Rust](https://img.shields.io/badge/rust-1.75%2B-orange)](#)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](#)

---

## 1. 项目简介

CryptoLab 把课程要求的 15 种密码算法**手写实现**在 Rust 中，通过 PyO3 暴露给 Python 服务端，再由 FastAPI 包装成 REST API，最后由 Vue3 前端提供可视化演示。

```
┌──────────────────────────────────────────────────────────────┐
│  L6 表示层  Vue3 + Element Plus / Swagger UI                  │
│  L5 网关层  Nginx + HTTPS 终结 + 限流                          │
│  L4 接口层  FastAPI + JWT + 参数校验 + 统一响应                │
│  L3 服务层  业务编排 / 密钥管理 / 审计                          │
│  L2 算法层  Rust 核心算法库 ─ PyO3 ─► Python                   │
│  L1 数据层  PostgreSQL + Redis                                │
└──────────────────────────────────────────────────────────────┘
```

完整设计见 `../系统设计方案.md`。

---

## 2. 首次使用（重要：依赖隔离）

**所有依赖必须落到项目目录内**，不写入 `~/.cargo`、`~/.rustup`、系统 Python、全局 npm。原因：

1. 学生机器上同时跑多门课程，全局工具链会互相冲突；
2. 提交评审时方便整个目录打包；
3. 出问题时整体 `rm -rf` 即可恢复，不留残骸。

### 一键初始化（Linux / macOS / WSL / Git Bash）

```bash
# 1. 进入项目根目录后，先把环境变量打到当前 shell
source scripts/env.sh

# 2. 安装本地 Rust 工具链 + Python venv + 前端依赖
bash scripts/setup.sh
```

### Windows 原生 PowerShell

```powershell
# scripts/env.ps1 与 scripts/setup.ps1 是 PowerShell 等价版本
. .\scripts\env.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1
```

执行完后你应该看到以下目录全部位于项目内：

```
.cargo-home/      # Rust 注册表缓存 + cargo install 的二进制
.rustup-home/     # Rust 工具链
.venv/            # Python 虚拟环境
frontend/node_modules/   # 前端依赖
.npm-cache/       # npm 缓存
```

> **每次新开终端**都需要再次 `source scripts/env.sh`（或 `. .\scripts\env.ps1`）。
> 推荐使用 `direnv` 让其自动加载。

---

## 3. 日常命令速查

| 操作                | 命令                                                |
| ------------------- | --------------------------------------------------- |
| 编译 Rust 核心库    | `bash scripts/build-rust.sh`                        |
| 启动 Python API     | `cd api_server && uvicorn app.main:app --reload`    |
| 启动前端 dev server | `cd frontend && npm run dev`                        |
| 跑全部测试          | `bash scripts/test-all.sh`                          |
| 性能基准            | `bash scripts/bench.sh`                             |
| 容器化一键启动      | `docker compose -f deploy/docker-compose.yml up -d` |
| Rust 格式化         | `cargo fmt --all` (in `rust_core/`)                 |
| Rust lint           | `cargo clippy --all-targets -- -D warnings`         |
| Python 格式化       | `ruff format api_server`                            |
| Python lint         | `ruff check api_server && mypy api_server/app`      |

---

## 4. 目录速览

```
CryptoLab/
├── rust_core/        # Rust 核心算法 + PyO3 绑定
├── api_server/       # FastAPI 服务端
├── frontend/         # Vue3 演示前端
├── deploy/           # Docker / Nginx 部署配置
├── scripts/          # 一键化脚本（env / setup / build / test / bench）
├── docs/             # 设计文档与报告（占位）
├── benchmarks/       # criterion 性能基准（占位）
├── .cargo/           # Cargo 项目级配置
├── .claude/          # Claude Code 项目级设置 + slash command
├── CLAUDE.md         # 给 Claude Code 的项目说明
└── README.md         # 本文件
```

---

## 5. 当前状态

本仓库目前处于 **init 阶段**：
- 所有目录结构、依赖声明、接口签名、模块路径已就位，工程可编译；
- 算法函数体均为 `todo!()` / `raise NotImplementedError`，等待逐个实现；
- 数据库迁移、Docker Compose、CI 配置已就绪。

下一步实现顺序参考 `系统设计方案.md` 第十部分的实施建议（14 天关键路径）。

---

## 6. License

MIT — 详见 [LICENSE](./LICENSE)。

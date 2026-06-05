---
description: 对全项目运行格式化与静态检查
---

按以下顺序运行 lint / format：

1. **Rust 格式化**：`cargo fmt --manifest-path rust_core/Cargo.toml --all`
2. **Rust clippy**：`cargo clippy --manifest-path rust_core/Cargo.toml --all-targets -- -D warnings`
3. **Python 格式化**：`ruff format api_server`
4. **Python lint**：`ruff check api_server --fix`
5. **Python 类型检查**：`mypy api_server/app`
6. **前端 lint**（如果 `frontend/package.json` 里有 `lint` 脚本）：`cd frontend && npm run lint`

把每一步的修复条数与剩余错误数汇总成一张表。如果有 mypy 错误，列出文件:行号。

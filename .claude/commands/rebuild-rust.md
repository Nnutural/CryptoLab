---
description: 重新编译 Rust 核心库并生成 Python 扩展（maturin develop）
---

当 `rust_core/src/` 下源码或 `Cargo.toml` 依赖有变化时，运行：

1. `source scripts/env.sh`（确保 CARGO_HOME 指向项目内）
2. `bash scripts/build-rust.sh`

该脚本本质上做了：
- `cd rust_core`
- `maturin develop --release`（自动把生成的 `.so` / `.pyd` 装进项目的 `.venv` 里，供 Python 侧 `import cryptolab_core`）

如果 maturin 找不到 Python 解释器，确认 `.venv` 已激活（`source .venv/bin/activate` 或 PowerShell 等价）。

构建完成后，运行 `python -c "import cryptolab_core; print(cryptolab_core.__doc__)"` 做 smoke test。

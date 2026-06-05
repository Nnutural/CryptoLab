---
description: 运行 CryptoLab 全栈测试（Rust + Python + 集成）
---

请运行 CryptoLab 的全部测试套件，按如下顺序：

1. **确认环境隔离**：检查 `$CARGO_HOME`、`$RUSTUP_HOME`、`which python` 是否指向项目内路径。如果未设置，先 `source scripts/env.sh`。
2. **Rust 单元测试**：`cargo test --manifest-path rust_core/Cargo.toml --all-features`
3. **Rust lint**：`cargo clippy --manifest-path rust_core/Cargo.toml --all-targets -- -D warnings`
4. **重新构建 Python 扩展**（如 Rust 源码有变化）：`bash scripts/build-rust.sh`
5. **Python 测试**：`pytest api_server/tests -v`
6. **Python lint**：`ruff check api_server && mypy api_server/app`

每一步如果失败，**立即停止**并把失败输出贴给我，不要静默继续。最后给我一个 pass/fail 汇总表。

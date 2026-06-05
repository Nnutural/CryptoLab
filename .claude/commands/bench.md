---
description: 运行 criterion 性能基准并汇总
---

运行性能基准：

1. 确认环境：`source scripts/env.sh`
2. 跑 Rust criterion 基准：`bash scripts/bench.sh`（等价于 `cargo bench --manifest-path rust_core/Cargo.toml`）
3. 基准结果会写入 `rust_core/target/criterion/`。打开 `target/criterion/report/index.html` 可查看图表。
4. 与历史结果对比：如果存在 `benchmarks/baseline.json`，请用 `cargo bench -- --baseline baseline` 并报告回归项。

输出格式：每个算法列出 throughput（MB/s）与 ns/op。如果某项相对前次基准退化超过 10%，**显著标出**并给我看堆栈定位建议。

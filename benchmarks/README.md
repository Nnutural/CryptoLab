# Benchmarks

Criterion-based performance benchmarks for the Rust core. Each algorithm
gets its own `bench_<algo>.rs` file added to `rust_core/Cargo.toml`'s
`[[bench]]` section once the algorithm is implemented.

Run:
```bash
source ../scripts/env.sh
bash ../scripts/bench.sh
```

Reports land in `rust_core/target/criterion/report/index.html`.

The HTTP-side throughput probe (`/api/v1/benchmark/{algo}`) is a thin
shim around the same primitives and is intended for in-browser
visualization, not for canonical numbers.

# CryptoLab Stage A Progress Delta

- 修复时间：2026-06-29 18:20:34 +08:00
- 范围：Target/3.md 阶段 A：清尾巴

## 修改文件清单

- `api_server/app/services/demo_service.py`：删除未引用的旧占位服务文件。
- `CLAUDE.md`：更新 benchmark 支持范围、metrics router 状态、前端 test 命令和最新测试数量。
- `frontend/package.json`：新增 `"test": "tsc -b --pretty false"`。
- `docs/progress_evidence/docker_build_stage_a.log`：保存本次 Docker build 完整输出。
- `docs/PROGRESS_DELTA.md`：本文件。

开工前已有但本次未回滚的工作树状态：`.codegraph/daemon.pid` 已删除，`README.md` 与 `cryptolab.db` 已修改，`docs/PROGRESS.md` 与 `docs/progress_evidence/` 未跟踪。

## 修复项

### demo_service.py 占位清理

- 执行 `rg -n "demo_service" api_server`，无命中。
- 确认实际 demo router 使用 `app.services.demos_service`。
- 删除未引用的 `api_server/app/services/demo_service.py`。
- 删除后 `rg -n "NotImplementedError|raise NotImplemented" api_server` 为 0 命中。

### CLAUDE.md benchmark 描述

- 移除过时的 “Benchmark note: backend benchmark service currently supports SHA-256 only.”。
- 按 `api_server/app/services/benchmark_service.py` 更新实际支持范围：
  `aes`, `aes_ecb`, `aes_gcm`, `sm4`, `sm4_ecb`, `rc6`, `rc6_ecb`,
  `sha1`, `sha256`, `sha512`, `sha3_256`, `ripemd160`,
  `hmac`, `hmac_sha256`, `pbkdf2`,
  `rsa_keygen`, `rsa_encrypt`, `rsa_decrypt`, `rsa_sign`, `rsa_verify`,
  `ecc_keygen`, `ecdsa_keygen`, `ecdsa_sign`, `ecdsa_verify`。
- 补充最新进度证据：Rust `53 passed; 0 failed; 3 ignored`，API `254 passed, 1 deselected`。
- 明确 Docker compose config 有证据，但 build 证据取决于 Docker daemon 和网络状态。
- `rg -n "SHA-256 only|supports SHA-256 only|Benchmark note" CLAUDE.md` 为 0 命中。

### npm test 脚本

- 在 `frontend/package.json` 增加 `"test": "tsc -b --pretty false"`。
- `npm test` 已通过，关键输出：

```text
> cryptolab-frontend@0.1.0 test
> tsc -b --pretty false
```

### Docker build

- `docker info` 成功，Docker daemon 可用。
- 已执行 `docker compose -f deploy/docker-compose.yml build`。
- 完整输出保存到 `docs/progress_evidence/docker_build_stage_a.log`。
- 构建失败，失败点是 `rust-builder` 镜像中 `apt-get install python3-pip` 下载 Debian 包时返回 502：

```text
Err:33 http://deb.debian.org/debian bookworm/main amd64 python3-pip all 23.0.1+dfsg-1
  502  Bad Gateway [IP: 146.75.114.132 80]
E: Failed to fetch http://deb.debian.org/debian/pool/main/p/python-pip/python3-pip_23.0.1%2bdfsg-1_all.deb  502  Bad Gateway [IP: 146.75.114.132 80]
failed to solve: process "/bin/sh -c apt-get update && apt-get install -y --no-install-recommends         python3 python3-dev python3-pip pkg-config     && rm -rf /var/lib/apt/lists/*" did not complete successfully: exit code: 100
```

## 验证命令与关键输出

```text
rg -n "NotImplementedError|raise NotImplemented" api_server
# 0 matches, rg exit code 1
```

```text
rg -n "TODO|FIXME" api_server/app rust_core/src frontend/src
# 0 matches, rg exit code 1
```

```text
rg -n "SHA-256 only|supports SHA-256 only|Benchmark note" CLAUDE.md
# 0 matches, rg exit code 1
```

```text
cd frontend
npm test

> cryptolab-frontend@0.1.0 test
> tsc -b --pretty false
```

```text
cd api_server
pytest tests/test_demos.py tests/test_router_boundaries.py -q
......                                                                   [100%]
6 passed in 0.60s
```

说明：第一次直接运行 `pytest tests/test_demos.py tests/test_router_boundaries.py -q` 时命中了系统 Python `E:\Python\Python312\python.exe`，缺少 `jwt`，报 `ModuleNotFoundError: No module named 'jwt'`。随后使用项目虚拟环境 `api_server\.venv\Scripts\python.exe -m pytest ...` 通过。

```text
git status --short
 D .codegraph/daemon.pid
 M CLAUDE.md
 D api_server/app/services/demo_service.py
 M cryptolab.db
 M frontend/package.json
?? docs/PROGRESS.md
?? docs/progress_evidence/
```

```text
git diff --stat
 .codegraph/daemon.pid                   |   6 -----
 CLAUDE.md                               |   7 +++---
 api_server/app/services/demo_service.py |  40 --------------------------------
 cryptolab.db                            | Bin 69632 -> 69632 bytes
 frontend/package.json                   |   1 +
 5 files changed, 5 insertions(+), 49 deletions(-)
```

## 剩余风险

- Docker build 未通过；当前失败是 Debian apt 502 网络/镜像源问题，需要在网络稳定或更换 apt mirror 后重跑。
- `cryptolab.db` 在开工前已有本地修改，且后续测试可能继续影响本地数据库状态；本次未回滚。
- `.codegraph/daemon.pid` 删除、`README.md` 修改和 `docs/PROGRESS.md` 未跟踪均为开工前已有状态；本次未处理这些无关改动。
- `npm test` 当前是 TypeScript 编译 smoke，不是浏览器或组件测试。

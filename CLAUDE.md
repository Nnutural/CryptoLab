# CLAUDE.md — CryptoLab

Project memory for Claude Code. Keep this file short: it is loaded into every session.

## Project

CryptoLab is a BUPT secure-programming midterm project: hand-written cryptographic primitives in Rust, exposed through PyO3, served by FastAPI, and exercised from a React teaching UI.

## Architecture

Two-layer implementation:

- **Core layer**: `rust_core/` implements algorithms and exposes `cryptolab_core` via PyO3.
- **Service layer**: `api_server/` wraps the Rust core with auth, key storage, audit, rate limiting, and REST APIs.
- **UI layer**: `frontend/` is a React 18 + Vite 6 + Tailwind 4 + Radix UI app with 12 API-backed views.

```text
CryptoLab/
├── rust_core/                 # Rust primitives + PyO3 extension
│   ├── Cargo.toml
│   └── src/
│       ├── ffi.rs             # all #[pyfunction] bindings
│       ├── symmetric/         # AES, SM4, RC6
│       ├── hash/              # SHA1/2/3, RIPEMD, HMAC, PBKDF2
│       ├── encoding/          # Base64, UTF-8
│       ├── pubkey/            # RSA, ECC, ECDSA, demos
│       └── modes/             # ECB, CBC, CTR, GCM
├── api_server/                # FastAPI + Pydantic + SQLAlchemy
│   ├── pyproject.toml
│   ├── alembic/
│   └── app/
│       ├── main.py            # middleware + /api/v1 routers
│       ├── routers/           # HTTP layer
│       ├── schemas/           # DTOs
│       ├── services/          # orchestration, key store, Rust calls
│       ├── middleware/        # trace, rate limit, JWT, audit
│       └── models/            # users, key_store, operation_logs
├── frontend/                  # React 18 + Vite 6 + Tailwind 4
│   └── src/{api,views,components,stores}/
├── deploy/                    # Dockerfiles, compose, nginx
├── scripts/                   # env/setup/build/test/bench
└── .codex/AGENTS.md           # longer Chinese guide for Codex
```

## Command Quick Reference

PowerShell is the primary local shell on this workspace.

| Task | Command |
| --- | --- |
| Load isolated env | `. .\scripts\env.ps1` |
| First setup | `powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1` |
| Build Rust extension | `powershell -ExecutionPolicy Bypass -File .\scripts\build-rust.ps1` |
| Rust tests | `cargo test --manifest-path rust_core/Cargo.toml` |
| Rust lint | `cargo clippy --manifest-path rust_core/Cargo.toml -- -D warnings` |
| Rust format | `cargo fmt --manifest-path rust_core/Cargo.toml --all` |
| API dev server | `uvicorn app.main:app --reload --app-dir api_server` |
| API tests | `pytest api_server/tests` |
| API lint/types | `ruff check api_server; mypy api_server/app` |
| Frontend dev server | `cd frontend; npm run dev` |
| Frontend build/typecheck | `cd frontend; npm run build` or `npx tsc --noEmit` |
| All tests | `powershell -ExecutionPolicy Bypass -File .\scripts\test-all.ps1` |
| Benchmark | `powershell -ExecutionPolicy Bypass -File .\scripts\bench.ps1` |
| Docker stack | `docker compose -f deploy/docker-compose.yml up -d` |
| DB migration | `cd api_server; alembic upgrade head` |

## Dependency Isolation

- Run `. .\scripts\env.ps1` before build/test commands in every new terminal.
- Rust uses project-local `./.cargo-home` and `./.rustup-home`.
- Python uses project-local `./.venv` and the local Rust extension from `maturin develop`.
- npm uses `frontend/.npmrc` with project-local cache/prefix; do not install global project deps.

## Current Stack

| Area | Current state |
| --- | --- |
| Frontend | React 18.3, Vite 6.3, TypeScript 5.7, Tailwind 4.1, Radix UI; 12 React views under `frontend/src/views/`. |
| API | FastAPI 0.110, Pydantic 2.6, SQLAlchemy 2.0, Redis 5, PyJWT, Alembic, structlog. |
| Security infra | JWT auth, user system, Redis rate limit, audit logging, HKDF-SHA256 KEK, AES-256-GCM envelope encryption for key material. |
| Rust core | PyO3 0.20, Rust 1.75, handwritten primitives with reference crates only for validation/tests. |

## Implementation Status

- Implemented Rust primitives: AES, SM4, RC6, ECB/CBC/CTR/GCM, SHA1/SHA2/SHA3, RIPEMD-160, HMAC, PBKDF2, Base64, UTF-8, RSA-1024 OAEP/PSS, ECC secp160r1, ECDSA, demo helpers.
- Remaining Rust `todo!()`: none in algorithm modules.
- API routers present: `auth`, `symmetric`, `hash`, `encoding`, `pubkey`, `scenarios`, `keys`, `audit`, `demos`, `benchmark`.
- Frontend views present: Dashboard, Symmetric, Hash, HMAC/PBKDF2, Encoding, RSA, ECC, Keys, Audit, Benchmark, Demos, Scenarios.
- API contract note: frontend is adapted to current backend DTOs; do not rename backend fields casually.
- Benchmark note: backend benchmark service currently supports SHA-256 only.

## Security Red Lines

- Never log plaintext secrets, keys, passwords, JWTs, or private key material.
- Use constant-time compare for MACs, tags, signatures, and digest equality checks.
- Use OS CSPRNG only: Rust `OsRng`, Python `secrets`.
- Private keys and symmetric keys must be KEK-wrapped before database storage.
- JWTs must expire; logout must blacklist token IDs in Redis until expiry.
- ECDSA production signing must use deterministic RFC 6979-style nonce derivation.
- RSA production paths must use OAEP/PSS and exponent >= 65537; raw/e=3 belongs only in demos.
- SQL must go through SQLAlchemy parameterization; no string-concatenated SQL.
- CORS production config must use explicit origins, never `"*"`.
- Demo endpoints must keep unsafe-parameter warnings and access controls.

## Module Boundaries

- Rust algorithm modules know nothing about HTTP, JSON, SQL, JWT, or FastAPI.
- PyO3 exports live in `rust_core/src/ffi.rs`; algorithm modules expose pure Rust APIs.
- Routers parse/authenticate and call services; routers must not reach into ORM models directly.
- Services orchestrate DB, audit, key loading, and Rust calls; raise `CryptoAPIException` for API errors.
- Frontend API calls belong in `frontend/src/api/`; React views should not use raw `axios`.

## Coding Style

- Follow existing local patterns; keep edits scoped.
- Rust: `cargo fmt`, `clippy -D warnings`, no production `unwrap()`/`expect()` unless genuinely infallible.
- Python: `ruff format`, `ruff check`, strict typing where practical, service-layer business logic.
- TypeScript: React function components, strict types where useful, no broad UI refactors during API fixes.

## Read First in a New Session

1. `CLAUDE.md` for constraints and current status.
2. `.codex/AGENTS.md` for detailed workflows, API tables, and task recipes.
3. The specific router/schema/service/view files for the feature being changed.

## Before Changing APIs

- Compare `frontend/src/api/*.ts` and view call sites against `api_server/app/routers`, `schemas`, and `services`.
- If the mismatch is frontend-fixable, adapt the frontend; avoid backend contract churn.
- If Rust is involved, trace `service -> cryptolab_core.<fn> -> rust_core/src/ffi.rs -> rust_core/src/<group>/<algo>.rs`.

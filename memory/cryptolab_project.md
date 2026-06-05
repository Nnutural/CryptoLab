---
name: cryptolab-project
description: CryptoLab — BUPT semester-6 secure-programming midterm project. Hand-written crypto algorithms with engineered service stack.
metadata:
  type: project
---

CryptoLab is the midterm assignment for BUPT 信息安全 / 安全编程 课程 (semester 6, 2026 spring). User is implementing 15 algorithms (AES, SM4, RC6, SHA1/2/3, RIPEMD, HMAC, PBKDF2, Base64, UTF-8, RSA-1024, ECC-160, ECDSA) by hand in Rust, exposed via PyO3 to a FastAPI service, with a Vue3 demo frontend and Docker Compose deploy. Initialized on 2026-06-06.

**Why:** assignment grading rewards engineering depth (architecture, audit, container, attack demos) over "调库交差"; aim is 90~100 score band.

**How to apply:** when working in this project, default to the六层分层 architecture (L1 data → L6 presentation). Algorithms live in `rust_core/` and must not touch HTTP types. API routers must not touch DB sessions directly — go through `services/`. Audit log only stores SHA-256 of input/output, never plaintext.

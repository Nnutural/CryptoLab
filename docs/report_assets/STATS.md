# CryptoLab 项目统计汇总

生成时间：2026-06-29 21:15:36 Asia/Shanghai  
基于 commit hash：`7a1c3f60933c60fc682958059662b4a486733bc1`  
工作树状态：dirty（`git status --short` 摘要：M cryptolab.db<br> M docs/report_assets/FIGURE_INDEX.md<br> M frontend/src/views/DemosView.tsx<br> M scripts/figures/check_figures.py<br> M scripts/figures/plot_algorithm_coverage_matrix.R<br> M scripts/figures/plot_cross_validation_evidence.R<br> M scripts/figures/run_benchmarks.py<br>?? docs/report_assets/FIGURE_QA.md<br>?? docs/report_assets/FRONT_SCREENSHOT_CLASSIFICATION.md<br>?? docs/report_assets/SCREENSHOT_CHECKLIST.md<br>?? docs/report_assets/SCREENSHOT_INDEX.md<br>?? docs/report_assets/STATS.md<br>?? docs/report_assets/data/algorithm_implementation.csv<br>?? docs/report_assets/data/api_endpoints.csv<br>?? docs/report_assets/data/code_lines_summary.csv<br>?? docs/report_assets/data/evidence_inventory.csv<br>?? docs/report_assets/data/fig2_algorithm_coverage_matrix.csv<br>?? docs/report_assets/data/fig2_algorithm_coverage_refined.csv<br>?? docs/report_assets/data/fig3_cross_validation_evidence.csv<br>?? docs/report_assets/data/fig3_cross_validation_refined.csv<br>?? docs/report_assets/data/fig3_cross_validation_refined_counts.csv<br>?? docs/report_assets/data/fig4_benchmark_raw.csv<br>?? docs/report_assets/data/fig4_benchmark_summary.csv<br>?? docs/report_assets/data/figure_assets_summary.csv<br>?? docs/report_assets/data/r_figures_status.txt<br>?? docs/report_assets/data/status_codes.csv<br>?? docs/report_assets/data/test_summary.csv<br>?? docs/report_assets/data/test_vector_sources.csv<br>?? docs/report_assets/figures/fig2_algorithm_coverage_matrix.png<br>?? docs/report_assets/figures/fig2_algorithm_coverage_matrix.svg<br>?? docs/report_assets/figures/fig2_algorithm_coverage_refined.pdf<br>?? docs/report_assets/figures/fig2_algorithm_coverage_refined.png<br>?? docs/report_assets/figures/fig3_cross_validation_evidence.png<br>?? docs/report_assets/figures/fig3_cross_validation_evidence.svg<br>?? docs/report_assets/figures/fig3_cross_validation_refined.pdf<br>?? docs/report_assets/figures/fig3_cross_validation_refined.png<br>?? docs/report_assets/figures/fig4_benchmark_performance.png<br>?? docs/report_assets/figures/fig4_benchmark_performance.svg<br>?? docs/report_assets/screenshots/<br>?? scripts/figures/plot_algorithm_coverage_refined.R<br>?? scripts/figures/plot_cross_validation_refined.R<br>?? scripts/stats/）

## 1. 统计口径

本文件由 `scripts/stats/generate_stats.py` 生成。统计来源包括当前 Git 输出、`rg --files` 文件清单、源码 AST/正则解析、已执行测试日志、Docker 日志、截图索引、图表 QA 报告与现有进度报告。所有 CSV 输出位于 `docs/report_assets/data/`，所有命令输出日志位于 `docs/report_assets/logs/`。

本轮命令执行情况：

- `git status --short`、`git rev-parse HEAD`、`rg --files` 已重新保存。
- Rust `cargo test --manifest-path rust_core\Cargo.toml --no-fail-fast` 通过。
- 用户指定的裸 `pytest --tb=no -q` 在当前 shell Python 中失败，原因为 `ModuleNotFoundError: No module named 'jwt'`；随后用项目 `.venv` 执行同等 pytest 通过。
- `frontend npm test` 执行 TypeScript smoke check，通过。
- `docker compose config` 通过；`docker compose build` 失败，失败阶段见 Docker 日志。
- 占位扫描：Rust=`无命中`；API=`无命中`；Frontend=`无命中`。

## 2. 总览数据表

| 类别 | 数值 | 证据 |
| --- | --- | --- |
| 算法实现 | 15/15 有实现证据；14 个为 ✅ | algorithm_implementation.csv; cargo_test_full.txt |
| API 端点 | 32/32 router 端点有 handler/service/test 证据 | api_endpoints.csv; endpoint_scan.txt |
| Rust 测试 | 53 passed, 0 failed, 3 ignored | docs/report_assets/logs/cargo_test_full.txt |
| API 测试 | .venv: 254 passed, 1 deselected；裸 pytest: errors=1 | pytest_venv_full.txt; pytest_full.txt |
| 前端检查 | npm test: ✅ (tsc smoke) | docs/report_assets/logs/npm_test_full.txt |
| 实验图 | 6 张 Fig.1-Fig.6 QA PASS | FIGURE_QA.md; figure_assets_summary.csv |
| 截图材料 | 已归档图片 28 个；前端 PNG 27 个 | SCREENSHOT_INDEX.md; FRONT_SCREENSHOT_CLASSIFICATION.md |
| Docker | config ✅；build ❌ | docker_compose_config.txt; docker_compose_build.txt |

## 3. 代码规模统计

| area | path_pattern | file_count | line_count | non_empty_line_count | test_file_count | evidence_command |
| --- | --- | --- | --- | --- | --- | --- |
| Rust core | rust_core/src/**/*.rs | 29 | 6093 | 5492 | 18 | Get-ChildItem -Recurse rust_core/src/**/*.rs; Python line counter in scripts/stats/generate_stats.py |
| API application | api_server/app/**/*.py | 61 | 5106 | 4128 | 0 | Get-ChildItem -Recurse api_server/app/**/*.py; Python line counter in scripts/stats/generate_stats.py |
| API tests | api_server/tests/**/*.py | 18 | 2935 | 2421 | 18 | Get-ChildItem -Recurse api_server/tests/**/*.py; Python line counter in scripts/stats/generate_stats.py |
| Frontend source | frontend/src/**/*.{ts,tsx,css} | 48 | 6577 | 6155 | 0 | Get-ChildItem -Recurse frontend/src/**/*.{ts,tsx,css}; Python line counter in scripts/stats/generate_stats.py |
| Docs | docs/**/* text assets | 94 | 9448 | 8802 | 19 | Get-ChildItem -Recurse docs/**/* text assets; Python line counter in scripts/stats/generate_stats.py |
| Scripts | scripts/**/* | 22 | 3371 | 2953 | 2 | Get-ChildItem -Recurse scripts/**/*; Python line counter in scripts/stats/generate_stats.py |

## 4. 算法与测试向量统计

### 4.1 算法实现统计

| layer | module | algorithm | subfeature | implementation_file | test_count | status | evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Rust core | encoding | Base64 | RFC 4648 encode/decode | rust_core/src/encoding/base64.rs | 4 | ✅ | cargo_test_full.txt; rg -n "todo!\(\)\|unimplemented!" rust_core/src/encoding/base64.rs |
| Rust core | encoding | UTF-8 | RFC 3629 encode/decode | rust_core/src/encoding/utf8.rs | 2 | ✅ | cargo_test_full.txt; rg -n "todo!\(\)\|unimplemented!" rust_core/src/encoding/utf8.rs |
| Rust core | hash | SHA1 | one-shot and streaming digest | rust_core/src/hash/sha1.rs | 3 | ✅ | cargo_test_full.txt; rg -n "todo!\(\)\|unimplemented!" rust_core/src/hash/sha1.rs |
| Rust core | hash | SHA256 | SHA-2 family, SHA-256 streaming | rust_core/src/hash/sha2.rs | 5 | ✅ | cargo_test_full.txt; rg -n "todo!\(\)\|unimplemented!" rust_core/src/hash/sha2.rs |
| Rust core | hash | SHA3 | SHA3-256 / SHA3-512 | rust_core/src/hash/sha3.rs | 2 | ✅ | cargo_test_full.txt; rg -n "todo!\(\)\|unimplemented!" rust_core/src/hash/sha3.rs |
| Rust core | hash | RIPEMD160 | RIPEMD-160 digest | rust_core/src/hash/ripemd.rs | 1 | ✅ | cargo_test_full.txt; rg -n "todo!\(\)\|unimplemented!" rust_core/src/hash/ripemd.rs |
| Rust core | hash | HMAC-SHA1 | RFC 2202 keyed MAC with constant-time verify path | rust_core/src/hash/hmac.rs | 1 | ✅ | cargo_test_full.txt; rg -n "todo!\(\)\|unimplemented!" rust_core/src/hash/hmac.rs |
| Rust core | hash | HMAC-SHA256 | RFC 4231 keyed MAC with constant-time verify path | rust_core/src/hash/hmac.rs | 2 | ✅ | cargo_test_full.txt; rg -n "todo!\(\)\|unimplemented!" rust_core/src/hash/hmac.rs |
| Rust core | hash | PBKDF2 | PBKDF2-HMAC-SHA256 | rust_core/src/hash/pbkdf2.rs | 2 | ✅ | cargo_test_full.txt; rg -n "todo!\(\)\|unimplemented!" rust_core/src/hash/pbkdf2.rs |
| Rust core | symmetric | AES | ECB/CBC/CTR/GCM plus verbose trace | rust_core/src/symmetric/aes.rs | 7 | ✅ | cargo_test_full.txt; rg -n "todo!\(\)\|unimplemented!" rust_core/src/symmetric/aes.rs |
| Rust core | symmetric | SM4 | ECB/CBC/CTR/GCM dispatch, GB/T single-block KAT | rust_core/src/symmetric/sm4.rs | 1 | ✅ | cargo_test_full.txt; rg -n "todo!\(\)\|unimplemented!" rust_core/src/symmetric/sm4.rs |
| Rust core | symmetric | RC6 | ECB/CBC implemented; GCM not exposed | rust_core/src/symmetric/rc6.rs | 1 | 🟡 | cargo_test_full.txt; rg -n "todo!\(\)\|unimplemented!" rust_core/src/symmetric/rc6.rs |
| Rust core | pubkey | RSA-1024 | keygen/encrypt/decrypt/sign/verify | rust_core/src/pubkey/rsa.rs | 8 | ✅ | cargo_test_full.txt; rg -n "todo!\(\)\|unimplemented!" rust_core/src/pubkey/rsa.rs |
| Rust core | pubkey | ECC-160 | secp160r1 point arithmetic and keygen | rust_core/src/pubkey/ecc.rs | 4 | ✅ | cargo_test_full.txt; rg -n "todo!\(\)\|unimplemented!" rust_core/src/pubkey/ecc.rs |
| Rust core | pubkey | ECDSA | secp160r1 sign/verify and deterministic nonce | rust_core/src/pubkey/ecdsa.rs | 2 | ✅ | cargo_test_full.txt; rg -n "todo!\(\)\|unimplemented!" rust_core/src/pubkey/ecdsa.rs |

### 4.2 测试向量来源统计

| algorithm | source_standard_or_library | test_file | test_case_name | count | evidence |
| --- | --- | --- | --- | --- | --- |
| Base64 | RFC 4648 | rust_core/src/encoding/base64.rs | rfc4648_section_10_vectors | 1 | docs/report_assets/logs/test_vector_sources_scan.txt; rg -n "RFC\|NIST\|FIPS\|OpenSSL\|PyCryptodome\|known vector\|test vector\|RFC 4648\|Wycheproof\|GM/T\|SM4" rust_core api_server docs |
| UTF-8 | RFC 3629 / Unicode scalar widths | rust_core/src/encoding/utf8.rs | encode_matches_rfc3629_widths; decode_rejects_ill_formed_rfc3629_sequences | 2 | docs/report_assets/logs/test_vector_sources_scan.txt; rg -n "RFC\|NIST\|FIPS\|OpenSSL\|PyCryptodome\|known vector\|test vector\|RFC 4648\|Wycheproof\|GM/T\|SM4" rust_core api_server docs |
| SHA1 | FIPS 180-4 | rust_core/src/hash/sha1.rs | fips_180_4_classic_vectors; million_a_vector | 2 | docs/report_assets/logs/test_vector_sources_scan.txt; rg -n "RFC\|NIST\|FIPS\|OpenSSL\|PyCryptodome\|known vector\|test vector\|RFC 4648\|Wycheproof\|GM/T\|SM4" rust_core api_server docs |
| SHA256/SHA2 | NIST / FIPS 180-4 | rust_core/src/hash/sha2.rs | sha256_nist_short_vectors; sha256_streaming_matches_one_shot_for_random_1mb | 2 | docs/report_assets/logs/test_vector_sources_scan.txt; rg -n "RFC\|NIST\|FIPS\|OpenSSL\|PyCryptodome\|known vector\|test vector\|RFC 4648\|Wycheproof\|GM/T\|SM4" rust_core api_server docs |
| SHA3 | FIPS 202 | rust_core/src/hash/sha3.rs | fips_202_sha3_256_vectors; fips_202_sha3_512_vectors | 2 | docs/report_assets/logs/test_vector_sources_scan.txt; rg -n "RFC\|NIST\|FIPS\|OpenSSL\|PyCryptodome\|known vector\|test vector\|RFC 4648\|Wycheproof\|GM/T\|SM4" rust_core api_server docs |
| RIPEMD160 | Original RIPEMD-160 vectors | rust_core/src/hash/ripemd.rs | original_ripemd160_vectors | 1 | docs/report_assets/logs/test_vector_sources_scan.txt; rg -n "RFC\|NIST\|FIPS\|OpenSSL\|PyCryptodome\|known vector\|test vector\|RFC 4648\|Wycheproof\|GM/T\|SM4" rust_core api_server docs |
| HMAC-SHA1 | RFC 2202 | rust_core/src/hash/hmac.rs | rfc_2202_hmac_sha1_vectors | 1 | docs/report_assets/logs/test_vector_sources_scan.txt; rg -n "RFC\|NIST\|FIPS\|OpenSSL\|PyCryptodome\|known vector\|test vector\|RFC 4648\|Wycheproof\|GM/T\|SM4" rust_core api_server docs |
| HMAC-SHA256 | RFC 4231 | rust_core/src/hash/hmac.rs | rfc_4231_hmac_sha256_vectors | 1 | docs/report_assets/logs/test_vector_sources_scan.txt; rg -n "RFC\|NIST\|FIPS\|OpenSSL\|PyCryptodome\|known vector\|test vector\|RFC 4648\|Wycheproof\|GM/T\|SM4" rust_core api_server docs |
| PBKDF2 | RFC 8018 / NIST SP 800-132 | rust_core/src/hash/pbkdf2.rs | pbkdf2_hmac_sha256_known_vectors | 1 | docs/report_assets/logs/test_vector_sources_scan.txt; rg -n "RFC\|NIST\|FIPS\|OpenSSL\|PyCryptodome\|known vector\|test vector\|RFC 4648\|Wycheproof\|GM/T\|SM4" rust_core api_server docs |
| AES | NIST SP 800-38A/38D; FIPS 197 | rust_core/src/symmetric/aes.rs | aes128_*_nist_*; fips_197_aes128_trace_matches_every_intermediate_state | 1 | docs/report_assets/logs/test_vector_sources_scan.txt; rg -n "RFC\|NIST\|FIPS\|OpenSSL\|PyCryptodome\|known vector\|test vector\|RFC 4648\|Wycheproof\|GM/T\|SM4" rust_core api_server docs |
| SM4 | GB/T 32907 | rust_core/src/symmetric/sm4.rs | gb_t_32907_appendix_a_single_block | 1 | docs/report_assets/logs/test_vector_sources_scan.txt; rg -n "RFC\|NIST\|FIPS\|OpenSSL\|PyCryptodome\|known vector\|test vector\|RFC 4648\|Wycheproof\|GM/T\|SM4" rust_core api_server docs |
| RC6 | RC6 paper appendix | rust_core/src/symmetric/rc6.rs | rc6_paper_appendix_b_zero_vector | 1 | docs/report_assets/logs/test_vector_sources_scan.txt; rg -n "RFC\|NIST\|FIPS\|OpenSSL\|PyCryptodome\|known vector\|test vector\|RFC 4648\|Wycheproof\|GM/T\|SM4" rust_core api_server docs |
| RSA-1024 | RFC 8017 | rust_core/src/pubkey/rsa.rs | rsa_keygen_oaep_pss_roundtrip; mgf1_is_deterministic | 2 | docs/report_assets/logs/test_vector_sources_scan.txt; rg -n "RFC\|NIST\|FIPS\|OpenSSL\|PyCryptodome\|known vector\|test vector\|RFC 4648\|Wycheproof\|GM/T\|SM4" rust_core api_server docs |
| ECC-160 | secp160r1 domain checks | rust_core/src/pubkey/ecc.rs | secp160r1_base_point_is_on_curve; order_times_base_point_is_infinity | 2 | docs/report_assets/logs/test_vector_sources_scan.txt; rg -n "RFC\|NIST\|FIPS\|OpenSSL\|PyCryptodome\|known vector\|test vector\|RFC 4648\|Wycheproof\|GM/T\|SM4" rust_core api_server docs |
| ECDSA | FIPS 186-4 / RFC 6979 | rust_core/src/pubkey/ecdsa.rs | sign_verify_roundtrip; tampering_fails | 2 | docs/report_assets/logs/test_vector_sources_scan.txt; rg -n "RFC\|NIST\|FIPS\|OpenSSL\|PyCryptodome\|known vector\|test vector\|RFC 4648\|Wycheproof\|GM/T\|SM4" rust_core api_server docs |

## 5. API 与状态码统计

### 5.1 API 端点

| module | method | path | handler_name | request_schema | response_schema | service_call | test_files | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| audit | GET | /api/v1/audit/logs | list_logs | None | APIResponse[list[OperationLogItem]] | audit_service.query_logs; audit_service.row_to_item | api_server/tests/conftest.py; api_server/tests/test_audit.py | ✅ |
| auth | POST | /api/v1/auth/login | login | LoginRequest | APIResponse[LoginResponse] | user_service.login | api_server/tests/conftest.py; api_server/tests/test_auth.py; api_server/tests/test_jwt.py; api_server/tests/test_keys.py; api_server/tests/test_rate_limit.py | ✅ |
| auth | POST | /api/v1/auth/logout | logout | None | APIResponse[None] | user_service.logout | api_server/tests/test_auth.py; api_server/tests/test_jwt.py | ✅ |
| auth | GET | /api/v1/auth/me | me | None | APIResponse[CurrentUserResponse] | user_service.me | api_server/tests/conftest.py; api_server/tests/test_aes_verbose.py; api_server/tests/test_audit.py; api_server/tests/test_auth.py; api_server/tests/test_benchmark.py; api_server/tests/test_cross_validation.py; api_server/tests/test_demos.py; api_server/tests/test_hash.py; api_server/tests/test_jwt.py; api_server/tests/test_keys.py; api_server/tests/test_metrics.py; api_server/tests/test_pubkey.py; api_server/tests/test_rate_limit.py; api_server/tests/test_router_boundaries.py; api_server/tests/test_symmetric.py | ✅ |
| auth | POST | /api/v1/auth/register | register | RegisterRequest | APIResponse[RegisterResponse] | user_service.register | api_server/tests/conftest.py; api_server/tests/test_auth.py; api_server/tests/test_jwt.py; api_server/tests/test_keys.py; api_server/tests/test_rate_limit.py | ✅ |
| benchmark | GET | /api/v1/benchmark/{algo} | benchmark | None | APIResponse[BenchmarkResult] | benchmark_service.measure | api_server/tests/test_benchmark.py; api_server/tests/test_metrics.py | ✅ |
| demos | POST | /api/v1/demos/ecb_image_leak | ecb_image_leak | demos_schema.EcbImageLeakRequest | 未显式声明 response_model | demos_service.EcbImageLeakService; demos_service.demo_access_dependency; demos_service.ok | api_server/tests/test_demos.py | 🟡 |
| demos | POST | /api/v1/demos/ecdsa_k_reuse | ecdsa_k_reuse | demos_schema.EcdsaKReuseRequest | 未显式声明 response_model | demos_service.EcdsaKReuseService; demos_service.demo_access_dependency; demos_service.ok | api_server/tests/test_demos.py | 🟡 |
| demos | POST | /api/v1/demos/pbkdf2_iteration_impact | pbkdf2_iteration_impact | demos_schema.Pbkdf2IterationImpactRequest | 未显式声明 response_model | demos_service.Pbkdf2IterationImpactService; demos_service.demo_access_dependency; demos_service.ok | api_server/tests/test_demos.py | 🟡 |
| demos | POST | /api/v1/demos/rsa_low_exponent | rsa_low_exponent | demos_schema.RsaLowExponentRequest | 未显式声明 response_model | demos_service.RsaLowExponentService; demos_service.demo_access_dependency; demos_service.ok | api_server/tests/test_demos.py | 🟡 |
| encoding | POST | /api/v1/encoding/base64/{op} | base64 | EncodeRequest \| DecodeRequest \| None | APIResponse[EncodeResponse \| DecodeResponse] | encoding_service.base64_decode; encoding_service.base64_encode | api_server/tests/test_aes_verbose.py; api_server/tests/test_cross_validation.py; api_server/tests/test_demos.py; api_server/tests/test_encoding.py; api_server/tests/test_metrics.py; api_server/tests/test_scenarios.py; api_server/tests/test_symmetric.py | ✅ |
| encoding | POST | /api/v1/encoding/utf8/{op} | utf8 | EncodeRequest \| DecodeRequest \| None | APIResponse[EncodeResponse \| DecodeResponse] | encoding_service.utf8_decode_op; encoding_service.utf8_encode_op | api_server/tests/test_cross_validation.py; api_server/tests/test_encoding.py | ✅ |
| hash | POST | /api/v1/hash/hmac/{algo} | hmac | HmacRequest | APIResponse[HmacResponse] | hash_service.hmac | api_server/tests/test_benchmark.py; api_server/tests/test_cross_validation.py; api_server/tests/test_hash.py | ✅ |
| hash | POST | /api/v1/hash/pbkdf2 | pbkdf2 | Pbkdf2Request | APIResponse[Pbkdf2Response] | hash_service.pbkdf2 | api_server/tests/test_benchmark.py; api_server/tests/test_cross_validation.py; api_server/tests/test_demos.py; api_server/tests/test_hash.py | ✅ |
| hash | POST | /api/v1/hash/{algo} | hash_ | HashRequest | APIResponse[HashResponse] | hash_service.hash_ | api_server/tests/test_cross_validation.py; api_server/tests/test_hash.py | ✅ |
| keys | GET | /api/v1/keys | list_keys | None | APIResponse[list[KeyListItem]] | key_service.list_for_user | api_server/tests/test_keys.py; api_server/tests/test_pubkey.py; api_server/tests/test_scenarios.py | ✅ |
| keys | DELETE | /api/v1/keys/{key_id} | revoke_key | None | APIResponse[None] | key_service.revoke | api_server/tests/test_keys.py; api_server/tests/test_pubkey.py; api_server/tests/test_scenarios.py | ✅ |
| keys | GET | /api/v1/keys/{key_id}/public | get_public_material | None | APIResponse[KeyPublicMaterialResponse] | key_service.fetch_public_material | api_server/tests/conftest.py; api_server/tests/test_benchmark.py; api_server/tests/test_cross_validation.py; api_server/tests/test_keys.py; api_server/tests/test_pubkey.py; api_server/tests/test_scenarios.py | ✅ |
| metrics | GET | /api/v1/metrics | list_metrics | None | APIResponse[list[AlgorithmMetricItem]] | metrics_service.query_metrics; metrics_service.row_to_item | api_server/tests/test_metrics.py | ✅ |
| pubkey | POST | /api/v1/pubkey/ecc/keygen | ecc_keygen | EccKeygenRequest | APIResponse[EccKeygenResponse] | pubkey_service.ecc_keygen | api_server/tests/test_benchmark.py; api_server/tests/test_cross_validation.py; api_server/tests/test_pubkey.py; api_server/tests/test_scenarios.py; api_server/tests/test_symmetric.py | ✅ |
| pubkey | POST | /api/v1/pubkey/ecdsa/sign | ecdsa_sign | EcdsaSignRequest | APIResponse[EcdsaSignResponse] | pubkey_service.ecdsa_sign | api_server/tests/test_benchmark.py; api_server/tests/test_cross_validation.py; api_server/tests/test_demos.py; api_server/tests/test_pubkey.py; api_server/tests/test_scenarios.py | ✅ |
| pubkey | POST | /api/v1/pubkey/ecdsa/verify | ecdsa_verify | EcdsaVerifyRequest | APIResponse[EcdsaVerifyResponse] | pubkey_service.ecdsa_verify | api_server/tests/test_benchmark.py; api_server/tests/test_cross_validation.py; api_server/tests/test_demos.py; api_server/tests/test_pubkey.py; api_server/tests/test_scenarios.py | ✅ |
| pubkey | POST | /api/v1/pubkey/rsa/decrypt | rsa_decrypt | RsaDecryptRequest | APIResponse[RsaDecryptResponse] | pubkey_service.rsa_decrypt | api_server/tests/test_benchmark.py; api_server/tests/test_cross_validation.py; api_server/tests/test_demos.py; api_server/tests/test_metrics.py; api_server/tests/test_pubkey.py; api_server/tests/test_scenarios.py; api_server/tests/test_symmetric.py | ✅ |
| pubkey | POST | /api/v1/pubkey/rsa/encrypt | rsa_encrypt | RsaEncryptRequest | APIResponse[RsaEncryptResponse] | pubkey_service.rsa_encrypt | api_server/tests/test_aes_verbose.py; api_server/tests/test_audit.py; api_server/tests/test_benchmark.py; api_server/tests/test_cross_validation.py; api_server/tests/test_demos.py; api_server/tests/test_jwt.py; api_server/tests/test_keys.py; api_server/tests/test_metrics.py; api_server/tests/test_pubkey.py; api_server/tests/test_scenarios.py; api_server/tests/test_symmetric.py | ✅ |
| pubkey | POST | /api/v1/pubkey/rsa/keygen | rsa_keygen | RsaKeygenRequest | APIResponse[RsaKeygenResponse] | pubkey_service.rsa_keygen | api_server/tests/test_benchmark.py; api_server/tests/test_cross_validation.py; api_server/tests/test_demos.py; api_server/tests/test_pubkey.py; api_server/tests/test_scenarios.py; api_server/tests/test_symmetric.py | ✅ |
| pubkey | POST | /api/v1/pubkey/rsa/sign | rsa_sign | RsaSignRequest | APIResponse[RsaSignResponse] | pubkey_service.rsa_sign | api_server/tests/test_benchmark.py; api_server/tests/test_cross_validation.py; api_server/tests/test_demos.py; api_server/tests/test_pubkey.py; api_server/tests/test_scenarios.py | ✅ |
| pubkey | POST | /api/v1/pubkey/rsa/verify | rsa_verify | RsaVerifyRequest | APIResponse[RsaVerifyResponse] | pubkey_service.rsa_verify | api_server/tests/test_benchmark.py; api_server/tests/test_cross_validation.py; api_server/tests/test_demos.py; api_server/tests/test_pubkey.py; api_server/tests/test_scenarios.py | ✅ |
| scenarios | POST | /api/v1/scenarios/secure_file_transfer/receive | secure_file_transfer_receive | SecureReceiveRequest | APIResponse[SecureReceiveResponse] | scenario_service.secure_file_receive | api_server/tests/test_scenarios.py | ✅ |
| scenarios | POST | /api/v1/scenarios/secure_file_transfer/send | secure_file_transfer_send | SecureSendRequest | APIResponse[SecureSendResponse] | scenario_service.secure_file_send | api_server/tests/test_scenarios.py | ✅ |
| symmetric | POST | /api/v1/symmetric/keygen | keygen | SymmetricKeygenRequest | APIResponse[dict] | symmetric_service.keygen | api_server/tests/test_aes_verbose.py; api_server/tests/test_benchmark.py; api_server/tests/test_cross_validation.py; api_server/tests/test_pubkey.py; api_server/tests/test_scenarios.py; api_server/tests/test_symmetric.py | ✅ |
| symmetric | POST | /api/v1/symmetric/{algo}/decrypt | decrypt | SymmetricDecryptRequest | APIResponse[SymmetricDecryptResponse] | symmetric_service.decrypt | api_server/tests/test_aes_verbose.py; api_server/tests/test_benchmark.py; api_server/tests/test_cross_validation.py; api_server/tests/test_metrics.py; api_server/tests/test_pubkey.py; api_server/tests/test_symmetric.py | ✅ |
| symmetric | POST | /api/v1/symmetric/{algo}/encrypt | encrypt | SymmetricEncryptRequest | APIResponse[SymmetricEncryptResponse] | symmetric_service.aes_encrypt_with_trace_op; symmetric_service.encrypt | api_server/tests/test_aes_verbose.py; api_server/tests/test_audit.py; api_server/tests/test_benchmark.py; api_server/tests/test_cross_validation.py; api_server/tests/test_demos.py; api_server/tests/test_jwt.py; api_server/tests/test_keys.py; api_server/tests/test_metrics.py; api_server/tests/test_pubkey.py; api_server/tests/test_symmetric.py | ✅ |

### 5.2 统一状态码

状态码定义共 `28` 项；引用计数按 `api_server/app` 源码中 `StatusCode.NAME` 出现次数统计，定义文件自身不计入引用数。

| code_name | value_or_http_status | definition_file | reference_count | reference_files |
| --- | --- | --- | --- | --- |
| OK | 1000 / HTTP 200 | api_server/app/core/status_codes.py | 24 | api_server/app/routers/audit.py; api_server/app/routers/auth.py; api_server/app/routers/benchmark.py; api_server/app/routers/encoding.py; api_server/app/routers/hash.py; api_server/app/routers/keys.py; api_server/app/routers/metrics.py; api_server/app/routers/pubkey.py; api_server/app/routers/scenarios.py; api_server/app/routers/symmetric.py; api_server/app/services/demos_service.py |
| PARAM_MISSING | 2001 / HTTP 400 | api_server/app/core/status_codes.py | 18 | api_server/app/core/exceptions.py; api_server/app/routers/encoding.py; api_server/app/routers/symmetric.py; api_server/app/services/demos_service.py; api_server/app/services/hash_service.py; api_server/app/services/pubkey_service.py; api_server/app/services/scenario_service.py; api_server/app/services/symmetric_service.py |
| KEY_LENGTH_INVALID | 2002 / HTTP 400 | api_server/app/core/status_codes.py | 5 | api_server/app/services/demos_service.py; api_server/app/services/scenario_service.py; api_server/app/services/symmetric_service.py |
| ENCODING_ERROR | 2003 / HTTP 400 | api_server/app/core/status_codes.py | 9 | api_server/app/routers/symmetric.py; api_server/app/services/demos_service.py; api_server/app/services/encoding_service.py; api_server/app/services/scenario_service.py |
| ALGORITHM_UNSUPPORTED | 2004 / HTTP 400 | api_server/app/core/status_codes.py | 16 | api_server/app/routers/symmetric.py; api_server/app/services/benchmark_service.py; api_server/app/services/demos_service.py; api_server/app/services/hash_service.py; api_server/app/services/scenario_service.py; api_server/app/services/symmetric_service.py |
| PADDING_INVALID | 2005 / HTTP 400 | api_server/app/core/status_codes.py | 2 | api_server/app/services/symmetric_service.py |
| ENCRYPT_FAILED | 3001 / HTTP 400 | api_server/app/core/status_codes.py | 3 | api_server/app/services/demos_service.py; api_server/app/services/pubkey_service.py; api_server/app/services/symmetric_service.py |
| DECRYPT_FAILED | 3002 / HTTP 400 | api_server/app/core/status_codes.py | 10 | api_server/app/services/key_service.py; api_server/app/services/pubkey_service.py; api_server/app/services/scenario_service.py; api_server/app/services/symmetric_service.py |
| SIGNATURE_INVALID | 3003 / HTTP 400 | api_server/app/core/status_codes.py | 2 | api_server/app/services/scenario_service.py |
| KEY_MISMATCH | 3004 / HTTP 400 | api_server/app/core/status_codes.py | 0 |  |
| UNAUTHENTICATED | 4001 / HTTP 401 | api_server/app/core/status_codes.py | 0 |  |
| TOKEN_EXPIRED | 4002 / HTTP 401 | api_server/app/core/status_codes.py | 0 |  |
| FORBIDDEN | 4003 / HTTP 403 | api_server/app/core/status_codes.py | 0 |  |
| AUTH_TOKEN_MISSING | 4101 / HTTP 401 | api_server/app/core/status_codes.py | 2 | api_server/app/middleware/auth.py |
| AUTH_TOKEN_MALFORMED | 4102 / HTTP 401 | api_server/app/core/status_codes.py | 2 | api_server/app/middleware/auth.py |
| AUTH_TOKEN_INVALID | 4103 / HTTP 401 | api_server/app/core/status_codes.py | 4 | api_server/app/middleware/auth.py; api_server/app/services/user_service.py |
| AUTH_TOKEN_EXPIRED | 4104 / HTTP 401 | api_server/app/core/status_codes.py | 1 | api_server/app/middleware/auth.py |
| AUTH_TOKEN_BLACKLISTED | 4105 / HTTP 401 | api_server/app/core/status_codes.py | 1 | api_server/app/middleware/auth.py |
| AUTH_LOGIN_FAILED | 4106 / HTTP 401 | api_server/app/core/status_codes.py | 2 | api_server/app/services/user_service.py |
| AUTH_USERNAME_EXISTS | 4107 / HTTP 409 | api_server/app/core/status_codes.py | 1 | api_server/app/services/user_service.py |
| KEY_NOT_OWNED | 4201 / HTTP 403 | api_server/app/core/status_codes.py | 1 | api_server/app/services/key_service.py |
| KEY_NOT_FOUND | 4202 / HTTP 404 | api_server/app/core/status_codes.py | 1 | api_server/app/services/key_service.py |
| KEY_TYPE_MISMATCH | 4203 / HTTP 400 | api_server/app/core/status_codes.py | 1 | api_server/app/services/key_service.py |
| KEY_PRIVATE_ACCESS_DENIED | 4204 / HTTP 403 | api_server/app/core/status_codes.py | 1 | api_server/app/services/key_service.py |
| INTERNAL | 5000 / HTTP 500 | api_server/app/core/status_codes.py | 6 | api_server/app/core/exceptions.py; api_server/app/services/demos_service.py; api_server/app/services/pubkey_service.py |
| RATE_LIMIT_EXCEEDED | 5001 / HTTP 429 | api_server/app/core/status_codes.py | 3 | api_server/app/middleware/rate_limit.py |
| DATABASE_ERROR | 5002 / HTTP 500 | api_server/app/core/status_codes.py | 9 | api_server/app/services/audit_service.py; api_server/app/services/key_service.py; api_server/app/services/metrics_service.py; api_server/app/services/user_service.py |
| CRYPTO_LIB_ERROR | 5003 / HTTP 500 | api_server/app/core/status_codes.py | 31 | api_server/app/services/benchmark_service.py; api_server/app/services/demos_service.py; api_server/app/services/encoding_service.py; api_server/app/services/hash_service.py; api_server/app/services/pubkey_service.py; api_server/app/services/scenario_service.py; api_server/app/services/symmetric_service.py |

## 6. 测试与构建统计

| test_layer | command | passed | failed | ignored_or_skipped | deselected | errors | status | evidence_log |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Rust core | cargo test --manifest-path rust_core\Cargo.toml --no-fail-fast | 53 | 0 | 3 | 0 | 0 | ✅ | docs/report_assets/logs/cargo_test_full.txt |
| API pytest (requested shell) | cd api_server; pytest --tb=no -q | 0 | 0 | 0 | 0 | 1 | ❌ | docs/report_assets/logs/pytest_full.txt |
| API pytest (.venv) | cd api_server; .\.venv\Scripts\python.exe -m pytest --tb=no -q | 254 | 0 | 0 | 1 | 0 | ✅ | docs/report_assets/logs/pytest_venv_full.txt |
| Frontend TypeScript | cd frontend; npm test | tsc smoke | 0 | 0 | 0 | 0 | ✅ | docs/report_assets/logs/npm_test_full.txt |
| Docker compose config | docker compose -f deploy\docker-compose.yml config | config parsed | 0 | 0 | 0 | 0 | ✅ | docs/report_assets/logs/docker_compose_config.txt |
| Docker compose build | docker compose -f deploy\docker-compose.yml build | 0 | 1 | 0 | 0 | 1 | ❌ | docs/report_assets/logs/docker_compose_build.txt |

Docker build 关键结论：`docs/report_assets/logs/docker_compose_build.txt` 显示 `rust-builder` 在 `maturin build` 阶段失败，Cargo 1.78.0 不支持依赖需要的 `edition2024` feature。该结果是构建失败证据，不是部署成功证据。

## 7. 实验图与数据资产统计

| figure_id | title | source_data | script | svg_path | png_path | qa_status | used_in_report | repro_command |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Fig. 1 | 测试验证总览图 | docs/report_assets/data/fig1_validation_overview.csv | scripts/figures/plot_validation_overview.py | docs/report_assets/figures/fig1_validation_overview.svg | docs/report_assets/figures/fig1_validation_overview.png | PASS | 建议纳入 PDF 正文 | .\.venv\Scripts\python.exe scripts\figures\plot_validation_overview.py |
| Fig. 2 | 算法覆盖与实现状态矩阵 | docs/report_assets/data/fig2_algorithm_coverage_matrix.csv | scripts/figures/plot_algorithm_coverage_matrix.R | docs/report_assets/figures/fig2_algorithm_coverage_matrix.svg | docs/report_assets/figures/fig2_algorithm_coverage_matrix.png | PASS | 建议纳入 PDF 正文 | Rscript scripts\figures\plot_algorithm_coverage_matrix.R |
| Fig. 3 | 交叉验证证据矩阵 | docs/report_assets/data/fig3_cross_validation_evidence.csv | scripts/figures/plot_cross_validation_evidence.R | docs/report_assets/figures/fig3_cross_validation_evidence.svg | docs/report_assets/figures/fig3_cross_validation_evidence.png | PASS | 建议纳入 PDF 正文 | Rscript scripts\figures\plot_cross_validation_evidence.R |
| Fig. 4 | Benchmark 性能结果图 | docs/report_assets/data/fig4_benchmark_summary.csv | scripts/figures/plot_benchmark_performance.py | docs/report_assets/figures/fig4_benchmark_performance.svg | docs/report_assets/figures/fig4_benchmark_performance.png | PASS | 建议纳入 PDF 正文 | .\.venv\Scripts\python.exe scripts\figures\plot_benchmark_performance.py |
| Fig. 5 | AES verbose trace 结果图 | docs/report_assets/data/fig5_aes_verbose_trace.csv | scripts/figures/plot_aes_verbose_trace.py | docs/report_assets/figures/fig5_aes_verbose_trace.svg | docs/report_assets/figures/fig5_aes_verbose_trace.png | PASS | 建议纳入 PDF 正文 | .\.venv\Scripts\python.exe scripts\figures\plot_aes_verbose_trace.py |
| Fig. 6 | 安全演示效果图 | docs/report_assets/data/fig6_ecb_leak_metrics.csv; docs/report_assets/data/fig6_pbkdf2_iterations.csv | scripts/figures/plot_security_demos.py | docs/report_assets/figures/fig6_security_demos.svg | docs/report_assets/figures/fig6_security_demos.png | PASS | 建议纳入 PDF 正文 | .\.venv\Scripts\python.exe scripts\figures\plot_security_demos.py |

## 8. 报告素材缺口

- 前端 AES verbose trace 截图 `P0_03_frontend_symmetric_aes_verbose_trace.png` 仍缺；可用 `fig5_aes_verbose_trace.png` 作非前端替代证据。
- Swagger `/docs` 与关键 API 成功响应仍缺 PNG 截图；当前只有日志证据。
- 测试、数据库、Docker 构建多数为日志证据，PNG 截图目录存在但 API/tests/database/docker 子目录为空或待人工补拍。
- Docker build 本轮失败，关键错误为 Cargo 1.78 无法解析 `edition2024` 依赖；不能作为构建成功证据。

截图清单存在性：

- `docs/report_assets/SCREENSHOT_CHECKLIST.md`：存在
- `docs/report_assets/SCREENSHOT_INDEX.md`：存在
- 前端运行截图：`docs/report_assets/screenshots/frontend/` 当前 PNG 数 `27`
- API 文档截图：需人工补拍，见 `SCREENSHOT_INDEX.md`
- 测试通过截图：当前以日志为主，PNG 需人工补拍
- 数据库表/审计日志截图：当前以日志为主，PNG 需人工补拍
- Docker 构建成功截图或日志：有失败日志，无成功截图

## 9. 可直接写入论文报告的数据表

### 9.1 系统实现规模表

| area | file_count | line_count | non_empty_line_count | test_file_count |
| --- | --- | --- | --- | --- |
| Rust core | 29 | 6093 | 5492 | 18 |
| API application | 61 | 5106 | 4128 | 0 |
| API tests | 18 | 2935 | 2421 | 18 |
| Frontend source | 48 | 6577 | 6155 | 0 |
| Docs | 94 | 9448 | 8802 | 19 |
| Scripts | 22 | 3371 | 2953 | 2 |

### 9.2 算法实现与验证表

| algorithm | subfeature | test_count | status | implementation_file |
| --- | --- | --- | --- | --- |
| Base64 | RFC 4648 encode/decode | 4 | ✅ | rust_core/src/encoding/base64.rs |
| UTF-8 | RFC 3629 encode/decode | 2 | ✅ | rust_core/src/encoding/utf8.rs |
| SHA1 | one-shot and streaming digest | 3 | ✅ | rust_core/src/hash/sha1.rs |
| SHA256 | SHA-2 family, SHA-256 streaming | 5 | ✅ | rust_core/src/hash/sha2.rs |
| SHA3 | SHA3-256 / SHA3-512 | 2 | ✅ | rust_core/src/hash/sha3.rs |
| RIPEMD160 | RIPEMD-160 digest | 1 | ✅ | rust_core/src/hash/ripemd.rs |
| HMAC-SHA1 | RFC 2202 keyed MAC with constant-time verify path | 1 | ✅ | rust_core/src/hash/hmac.rs |
| HMAC-SHA256 | RFC 4231 keyed MAC with constant-time verify path | 2 | ✅ | rust_core/src/hash/hmac.rs |
| PBKDF2 | PBKDF2-HMAC-SHA256 | 2 | ✅ | rust_core/src/hash/pbkdf2.rs |
| AES | ECB/CBC/CTR/GCM plus verbose trace | 7 | ✅ | rust_core/src/symmetric/aes.rs |
| SM4 | ECB/CBC/CTR/GCM dispatch, GB/T single-block KAT | 1 | ✅ | rust_core/src/symmetric/sm4.rs |
| RC6 | ECB/CBC implemented; GCM not exposed | 1 | 🟡 | rust_core/src/symmetric/rc6.rs |
| RSA-1024 | keygen/encrypt/decrypt/sign/verify | 8 | ✅ | rust_core/src/pubkey/rsa.rs |
| ECC-160 | secp160r1 point arithmetic and keygen | 4 | ✅ | rust_core/src/pubkey/ecc.rs |
| ECDSA | secp160r1 sign/verify and deterministic nonce | 2 | ✅ | rust_core/src/pubkey/ecdsa.rs |

### 9.3 API 端点覆盖表

| module | method | path | request_schema | response_schema | status |
| --- | --- | --- | --- | --- | --- |
| audit | GET | /api/v1/audit/logs | None | APIResponse[list[OperationLogItem]] | ✅ |
| auth | POST | /api/v1/auth/login | LoginRequest | APIResponse[LoginResponse] | ✅ |
| auth | POST | /api/v1/auth/logout | None | APIResponse[None] | ✅ |
| auth | GET | /api/v1/auth/me | None | APIResponse[CurrentUserResponse] | ✅ |
| auth | POST | /api/v1/auth/register | RegisterRequest | APIResponse[RegisterResponse] | ✅ |
| benchmark | GET | /api/v1/benchmark/{algo} | None | APIResponse[BenchmarkResult] | ✅ |
| demos | POST | /api/v1/demos/ecb_image_leak | demos_schema.EcbImageLeakRequest | 未显式声明 response_model | 🟡 |
| demos | POST | /api/v1/demos/ecdsa_k_reuse | demos_schema.EcdsaKReuseRequest | 未显式声明 response_model | 🟡 |
| demos | POST | /api/v1/demos/pbkdf2_iteration_impact | demos_schema.Pbkdf2IterationImpactRequest | 未显式声明 response_model | 🟡 |
| demos | POST | /api/v1/demos/rsa_low_exponent | demos_schema.RsaLowExponentRequest | 未显式声明 response_model | 🟡 |
| encoding | POST | /api/v1/encoding/base64/{op} | EncodeRequest \| DecodeRequest \| None | APIResponse[EncodeResponse \| DecodeResponse] | ✅ |
| encoding | POST | /api/v1/encoding/utf8/{op} | EncodeRequest \| DecodeRequest \| None | APIResponse[EncodeResponse \| DecodeResponse] | ✅ |
| hash | POST | /api/v1/hash/hmac/{algo} | HmacRequest | APIResponse[HmacResponse] | ✅ |
| hash | POST | /api/v1/hash/pbkdf2 | Pbkdf2Request | APIResponse[Pbkdf2Response] | ✅ |
| hash | POST | /api/v1/hash/{algo} | HashRequest | APIResponse[HashResponse] | ✅ |
| keys | GET | /api/v1/keys | None | APIResponse[list[KeyListItem]] | ✅ |
| keys | DELETE | /api/v1/keys/{key_id} | None | APIResponse[None] | ✅ |
| keys | GET | /api/v1/keys/{key_id}/public | None | APIResponse[KeyPublicMaterialResponse] | ✅ |
| metrics | GET | /api/v1/metrics | None | APIResponse[list[AlgorithmMetricItem]] | ✅ |
| pubkey | POST | /api/v1/pubkey/ecc/keygen | EccKeygenRequest | APIResponse[EccKeygenResponse] | ✅ |
| pubkey | POST | /api/v1/pubkey/ecdsa/sign | EcdsaSignRequest | APIResponse[EcdsaSignResponse] | ✅ |
| pubkey | POST | /api/v1/pubkey/ecdsa/verify | EcdsaVerifyRequest | APIResponse[EcdsaVerifyResponse] | ✅ |
| pubkey | POST | /api/v1/pubkey/rsa/decrypt | RsaDecryptRequest | APIResponse[RsaDecryptResponse] | ✅ |
| pubkey | POST | /api/v1/pubkey/rsa/encrypt | RsaEncryptRequest | APIResponse[RsaEncryptResponse] | ✅ |
| pubkey | POST | /api/v1/pubkey/rsa/keygen | RsaKeygenRequest | APIResponse[RsaKeygenResponse] | ✅ |
| pubkey | POST | /api/v1/pubkey/rsa/sign | RsaSignRequest | APIResponse[RsaSignResponse] | ✅ |
| pubkey | POST | /api/v1/pubkey/rsa/verify | RsaVerifyRequest | APIResponse[RsaVerifyResponse] | ✅ |
| scenarios | POST | /api/v1/scenarios/secure_file_transfer/receive | SecureReceiveRequest | APIResponse[SecureReceiveResponse] | ✅ |
| scenarios | POST | /api/v1/scenarios/secure_file_transfer/send | SecureSendRequest | APIResponse[SecureSendResponse] | ✅ |
| symmetric | POST | /api/v1/symmetric/keygen | SymmetricKeygenRequest | APIResponse[dict] | ✅ |
| symmetric | POST | /api/v1/symmetric/{algo}/decrypt | SymmetricDecryptRequest | APIResponse[SymmetricDecryptResponse] | ✅ |
| symmetric | POST | /api/v1/symmetric/{algo}/encrypt | SymmetricEncryptRequest | APIResponse[SymmetricEncryptResponse] | ✅ |

### 9.4 测试结果汇总表

| test_layer | command | passed | failed | ignored_or_skipped | deselected | errors | status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Rust core | cargo test --manifest-path rust_core\Cargo.toml --no-fail-fast | 53 | 0 | 3 | 0 | 0 | ✅ |
| API pytest (requested shell) | cd api_server; pytest --tb=no -q | 0 | 0 | 0 | 0 | 1 | ❌ |
| API pytest (.venv) | cd api_server; .\.venv\Scripts\python.exe -m pytest --tb=no -q | 254 | 0 | 0 | 1 | 0 | ✅ |
| Frontend TypeScript | cd frontend; npm test | tsc smoke | 0 | 0 | 0 | 0 | ✅ |
| Docker compose config | docker compose -f deploy\docker-compose.yml config | config parsed | 0 | 0 | 0 | 0 | ✅ |
| Docker compose build | docker compose -f deploy\docker-compose.yml build | 0 | 1 | 0 | 0 | 1 | ❌ |

### 9.5 实验图索引表

| figure_id | title | source_data | png_path | qa_status |
| --- | --- | --- | --- | --- |
| Fig. 1 | 测试验证总览图 | docs/report_assets/data/fig1_validation_overview.csv | docs/report_assets/figures/fig1_validation_overview.png | PASS |
| Fig. 2 | 算法覆盖与实现状态矩阵 | docs/report_assets/data/fig2_algorithm_coverage_matrix.csv | docs/report_assets/figures/fig2_algorithm_coverage_matrix.png | PASS |
| Fig. 3 | 交叉验证证据矩阵 | docs/report_assets/data/fig3_cross_validation_evidence.csv | docs/report_assets/figures/fig3_cross_validation_evidence.png | PASS |
| Fig. 4 | Benchmark 性能结果图 | docs/report_assets/data/fig4_benchmark_summary.csv | docs/report_assets/figures/fig4_benchmark_performance.png | PASS |
| Fig. 5 | AES verbose trace 结果图 | docs/report_assets/data/fig5_aes_verbose_trace.csv | docs/report_assets/figures/fig5_aes_verbose_trace.png | PASS |
| Fig. 6 | 安全演示效果图 | docs/report_assets/data/fig6_ecb_leak_metrics.csv; docs/report_assets/data/fig6_pbkdf2_iterations.csv | docs/report_assets/figures/fig6_security_demos.png | PASS |

### 9.6 报告素材清单表

| category | file_path | purpose | status | notes |
| --- | --- | --- | --- | --- |
| progress | docs/PROGRESS.md | 历史进度报告 | ✅ 非空 | 20932 bytes |
| progress | docs/PROGRESS_DELTA.md | Stage A 修复记录 | ✅ 非空 | 4988 bytes |
| stats | docs/report_assets/STATS.md | 本次统计汇总 | ✅ 生成 | 最终文件由本脚本写入；大小以文件系统当前值为准 |
| figures | docs/report_assets/FIGURE_INDEX.md | 图表索引 | ✅ 非空 | 11903 bytes |
| figures | docs/report_assets/FIGURE_QA.md | 图表质量检查 | ✅ 非空 | 1511 bytes |
| screenshots | docs/report_assets/SCREENSHOT_CHECKLIST.md | 截图清单 | ✅ 非空 | 20573 bytes |
| screenshots | docs/report_assets/SCREENSHOT_INDEX.md | 截图索引 | ✅ 非空 | 13625 bytes |
| screenshots | docs/report_assets/screenshots/frontend | 前端截图目录 | ✅ 存在 | 27 files |
| screenshots | docs/report_assets/screenshots/api | API 截图目录 | 🟡 空目录 | 如为空则需人工补拍 |
| screenshots | docs/report_assets/screenshots/tests | 测试截图目录 | 🟡 空目录 | 如为空则需人工补拍 |
| screenshots | docs/report_assets/screenshots/database | 数据库截图目录 | 🟡 空目录 | 如为空则需人工补拍 |
| screenshots | docs/report_assets/screenshots/docker | Docker 截图目录 | 🟡 空目录 | 如为空则需人工补拍 |
| logs | docs/report_assets/logs | 统计与验证日志目录 | ✅ 存在 | 29 files |
| progress_evidence | docs/progress_evidence | 早期进度证据目录 | ✅ 存在 | 36 files |
| progress_evidence | docs/progress_evidence/docker_build_stage_a.log | Stage A Docker build 日志 | ✅ 非空 | 可能不存在于当前树 |
| figures | docs/report_assets/figures/fig1_validation_overview.png | 实验图资产 | ✅ 非空 | 126562 bytes |
| figures | docs/report_assets/figures/fig1_validation_overview.svg | 实验图资产 | ✅ 非空 | 23910 bytes |
| figures | docs/report_assets/figures/fig2_algorithm_coverage_matrix.png | 实验图资产 | ✅ 非空 | 152727 bytes |
| figures | docs/report_assets/figures/fig2_algorithm_coverage_matrix.svg | 实验图资产 | ✅ 非空 | 26356 bytes |
| figures | docs/report_assets/figures/fig2_algorithm_coverage_refined.pdf | 实验图资产 | ✅ 非空 | 51797 bytes |
| ... |  |  |  | 其余 48 行见 CSV |


## 10. 复现命令

```powershell
Set-Location "D:\Nnutural\Desktop\BUPT_6\SecureProgrammingTechnologyandCaseDevelopment\期中作业\CryptoLab"
python scripts\stats\generate_stats.py
```

重新生成底层日志的核心命令：

```powershell
git status --short | Tee-Object docs\report_assets\logs\git_status.txt
git rev-parse HEAD | Tee-Object docs\report_assets\logs\git_head.txt
rg --files | Tee-Object docs\report_assets\logs\code_file_inventory.txt
cargo test --manifest-path rust_core\Cargo.toml --no-fail-fast 2>&1 | Tee-Object docs\report_assets\logs\cargo_test_full.txt | Select-Object -Last 80 | Tee-Object docs\report_assets\logs\cargo_test_tail.txt
Push-Location api_server; .\.venv\Scripts\python.exe -m pytest --tb=no -q 2>&1 | Tee-Object ..\docs\report_assets\logs\pytest_venv_full.txt | Select-Object -Last 80 | Tee-Object ..\docs\report_assets\logs\pytest_venv_tail.txt; Pop-Location
Push-Location frontend; npm test 2>&1 | Tee-Object ..\docs\report_assets\logs\npm_test_full.txt | Select-Object -Last 80 | Tee-Object ..\docs\report_assets\logs\npm_test_tail.txt; Pop-Location
docker compose -f deploy\docker-compose.yml config 2>&1 | Tee-Object docs\report_assets\logs\docker_compose_config.txt
docker compose -f deploy\docker-compose.yml build 2>&1 | Tee-Object docs\report_assets\logs\docker_compose_build.txt
```

## 附录 A：关键命令输出索引

| category | file_path | purpose | status | notes |
| --- | --- | --- | --- | --- |
| progress | docs/PROGRESS.md | 历史进度报告 | ✅ 非空 | 20932 bytes |
| progress | docs/PROGRESS_DELTA.md | Stage A 修复记录 | ✅ 非空 | 4988 bytes |
| stats | docs/report_assets/STATS.md | 本次统计汇总 | ✅ 生成 | 最终文件由本脚本写入；大小以文件系统当前值为准 |
| figures | docs/report_assets/FIGURE_INDEX.md | 图表索引 | ✅ 非空 | 11903 bytes |
| figures | docs/report_assets/FIGURE_QA.md | 图表质量检查 | ✅ 非空 | 1511 bytes |
| screenshots | docs/report_assets/SCREENSHOT_CHECKLIST.md | 截图清单 | ✅ 非空 | 20573 bytes |
| screenshots | docs/report_assets/SCREENSHOT_INDEX.md | 截图索引 | ✅ 非空 | 13625 bytes |
| screenshots | docs/report_assets/screenshots/frontend | 前端截图目录 | ✅ 存在 | 27 files |
| screenshots | docs/report_assets/screenshots/api | API 截图目录 | 🟡 空目录 | 如为空则需人工补拍 |
| screenshots | docs/report_assets/screenshots/tests | 测试截图目录 | 🟡 空目录 | 如为空则需人工补拍 |
| screenshots | docs/report_assets/screenshots/database | 数据库截图目录 | 🟡 空目录 | 如为空则需人工补拍 |
| screenshots | docs/report_assets/screenshots/docker | Docker 截图目录 | 🟡 空目录 | 如为空则需人工补拍 |
| logs | docs/report_assets/logs | 统计与验证日志目录 | ✅ 存在 | 29 files |
| progress_evidence | docs/progress_evidence | 早期进度证据目录 | ✅ 存在 | 36 files |
| progress_evidence | docs/progress_evidence/docker_build_stage_a.log | Stage A Docker build 日志 | ✅ 非空 | 可能不存在于当前树 |
| figures | docs/report_assets/figures/fig1_validation_overview.png | 实验图资产 | ✅ 非空 | 126562 bytes |
| figures | docs/report_assets/figures/fig1_validation_overview.svg | 实验图资产 | ✅ 非空 | 23910 bytes |
| figures | docs/report_assets/figures/fig2_algorithm_coverage_matrix.png | 实验图资产 | ✅ 非空 | 152727 bytes |
| figures | docs/report_assets/figures/fig2_algorithm_coverage_matrix.svg | 实验图资产 | ✅ 非空 | 26356 bytes |
| figures | docs/report_assets/figures/fig2_algorithm_coverage_refined.pdf | 实验图资产 | ✅ 非空 | 51797 bytes |
| figures | docs/report_assets/figures/fig2_algorithm_coverage_refined.png | 实验图资产 | ✅ 非空 | 177697 bytes |
| figures | docs/report_assets/figures/fig3_cross_validation_evidence.png | 实验图资产 | ✅ 非空 | 204062 bytes |
| figures | docs/report_assets/figures/fig3_cross_validation_evidence.svg | 实验图资产 | ✅ 非空 | 32502 bytes |
| figures | docs/report_assets/figures/fig3_cross_validation_refined.pdf | 实验图资产 | ✅ 非空 | 48383 bytes |
| figures | docs/report_assets/figures/fig3_cross_validation_refined.png | 实验图资产 | ✅ 非空 | 176130 bytes |
| figures | docs/report_assets/figures/fig4_benchmark_performance.png | 实验图资产 | ✅ 非空 | 229304 bytes |
| figures | docs/report_assets/figures/fig4_benchmark_performance.svg | 实验图资产 | ✅ 非空 | 67434 bytes |
| figures | docs/report_assets/figures/fig5_aes_verbose_trace.png | 实验图资产 | ✅ 非空 | 200144 bytes |
| figures | docs/report_assets/figures/fig5_aes_verbose_trace.svg | 实验图资产 | ✅ 非空 | 48557 bytes |
| figures | docs/report_assets/figures/fig6_security_demos.png | 实验图资产 | ✅ 非空 | 549145 bytes |
| figures | docs/report_assets/figures/fig6_security_demos.svg | 实验图资产 | ✅ 非空 | 118962 bytes |
| data | docs/report_assets/data/algorithm_implementation.csv | CSV/数据资产 | ✅ 非空 | 3572 bytes |
| data | docs/report_assets/data/api_endpoints.csv | CSV/数据资产 | ✅ 非空 | 14646 bytes |
| data | docs/report_assets/data/code_lines_summary.csv | CSV/数据资产 | ✅ 非空 | 1009 bytes |
| data | docs/report_assets/data/evidence_inventory.csv | CSV/数据资产 | ✅ 非空 | 8056 bytes |
| data | docs/report_assets/data/fig1_validation_overview.csv | CSV/数据资产 | ✅ 非空 | 808 bytes |
| data | docs/report_assets/data/fig2_algorithm_coverage_matrix.csv | CSV/数据资产 | ✅ 非空 | 2495 bytes |
| data | docs/report_assets/data/fig2_algorithm_coverage_refined.csv | CSV/数据资产 | ✅ 非空 | 2793 bytes |
| data | docs/report_assets/data/fig3_cross_validation_evidence.csv | CSV/数据资产 | ✅ 非空 | 4873 bytes |
| data | docs/report_assets/data/fig3_cross_validation_refined.csv | CSV/数据资产 | ✅ 非空 | 5457 bytes |
| data | docs/report_assets/data/fig3_cross_validation_refined_counts.csv | CSV/数据资产 | ✅ 非空 | 850 bytes |
| data | docs/report_assets/data/fig4_benchmark_raw.csv | CSV/数据资产 | ✅ 非空 | 16653 bytes |
| data | docs/report_assets/data/fig4_benchmark_summary.csv | CSV/数据资产 | ✅ 非空 | 2743 bytes |
| data | docs/report_assets/data/fig5_aes_verbose_trace.csv | CSV/数据资产 | ✅ 非空 | 3097 bytes |
| data | docs/report_assets/data/fig6_ecb_leak_metrics.csv | CSV/数据资产 | ✅ 非空 | 157 bytes |
| data | docs/report_assets/data/fig6_pbkdf2_iterations.csv | CSV/数据资产 | ✅ 非空 | 1992 bytes |
| data | docs/report_assets/data/figure_assets_summary.csv | CSV/数据资产 | ✅ 非空 | 2195 bytes |
| data | docs/report_assets/data/r_figures_status.txt | CSV/数据资产 | ✅ 非空 | 1578 bytes |
| data | docs/report_assets/data/status_codes.csv | CSV/数据资产 | ✅ 非空 | 6373 bytes |
| data | docs/report_assets/data/test_summary.csv | CSV/数据资产 | ✅ 非空 | 877 bytes |
| data | docs/report_assets/data/test_vector_sources.csv | CSV/数据资产 | ✅ 非空 | 4344 bytes |
| logs | docs/report_assets/logs/cargo_test_full.txt | 命令输出日志 | ✅ 非空 | 7009 bytes |
| logs | docs/report_assets/logs/cargo_test_tail.txt | 命令输出日志 | ✅ 非空 | 4699 bytes |
| logs | docs/report_assets/logs/code_file_inventory.txt | 命令输出日志 | ✅ 非空 | 18879 bytes |
| logs | docs/report_assets/logs/docker_compose_build.txt | 命令输出日志 | ✅ 非空 | 21524 bytes |
| logs | docs/report_assets/logs/docker_compose_config.txt | 命令输出日志 | ✅ 非空 | 4238 bytes |
| logs | docs/report_assets/logs/endpoint_scan.txt | 命令输出日志 | ✅ 非空 | 26542 bytes |
| logs | docs/report_assets/logs/git_head.txt | 命令输出日志 | ✅ 非空 | 42 bytes |
| logs | docs/report_assets/logs/git_status.txt | 命令输出日志 | ✅ 非空 | 2180 bytes |
| logs | docs/report_assets/logs/npm_test_full.txt | 命令输出日志 | ✅ 非空 | 62 bytes |
| logs | docs/report_assets/logs/npm_test_tail.txt | 命令输出日志 | ✅ 非空 | 62 bytes |
| logs | docs/report_assets/logs/pytest_full.txt | 命令输出日志 | ✅ 非空 | 362 bytes |
| logs | docs/report_assets/logs/pytest_tail.txt | 命令输出日志 | ✅ 非空 | 362 bytes |
| logs | docs/report_assets/logs/pytest_venv_full.txt | 命令输出日志 | ✅ 非空 | 370 bytes |
| logs | docs/report_assets/logs/pytest_venv_tail.txt | 命令输出日志 | ✅ 非空 | 370 bytes |
| logs | docs/report_assets/logs/source_inventory_depth2.txt | 命令输出日志 | ✅ 非空 | 193122 bytes |
| logs | docs/report_assets/logs/status_code_scan.txt | 命令输出日志 | ✅ 非空 | 25041 bytes |
| logs | docs/report_assets/logs/test_vector_sources_scan.txt | 命令输出日志 | ✅ 非空 | 84829 bytes |

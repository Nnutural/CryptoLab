# CryptoLab Cross-Validation Matrix

| 算法 | 第一重(KAT) | 第二重(库对照) | 用例数 | 全部通过? |
|------|-------------|-----------------|--------|----------|
| AES-128-ECB | ✅ NIST/FIPS | ✅ cryptography | 2 | ✅ |
| AES-128-CBC | ✅ NIST/FIPS | ✅ cryptography | 2 | ✅ |
| AES-128-CTR | ✅ NIST/FIPS | ✅ cryptography | 2 | ✅ |
| AES-128-GCM | ✅ NIST/FIPS | ✅ cryptography | 2 | ✅ |
| AES-192-ECB | ✅ NIST/FIPS | ✅ cryptography | 2 | ✅ |
| AES-192-CBC | ✅ NIST/FIPS | ✅ cryptography | 2 | ✅ |
| AES-192-CTR | ✅ NIST/FIPS | ✅ cryptography | 2 | ✅ |
| AES-192-GCM | ✅ NIST/FIPS | ✅ cryptography | 2 | ✅ |
| AES-256-ECB | ✅ NIST/FIPS | ✅ cryptography | 2 | ✅ |
| AES-256-CBC | ✅ NIST/FIPS | ✅ cryptography | 2 | ✅ |
| AES-256-CTR | ✅ NIST/FIPS | ✅ cryptography | 2 | ✅ |
| AES-256-GCM | ✅ NIST/FIPS | ✅ cryptography | 2 | ✅ |
| SM4-ECB | ✅ GB/T | ✅ gmssl | 2 | ✅ |
| SM4-CBC | ✅ GB/T | ✅ gmssl | 2 | ✅ |
| RC6 | ✅ Rivest/Krovetz | ❌ N/A | 4 | ✅ KAT-only |
| SHA1 | ✅ RFC/NIST | ✅ hashlib | 6 | ✅ |
| SHA224 | ✅ RFC/NIST | ✅ hashlib | 6 | ✅ |
| SHA256 | ✅ RFC/NIST | ✅ hashlib | 6 | ✅ |
| SHA384 | ✅ RFC/NIST | ✅ hashlib | 6 | ✅ |
| SHA512 | ✅ RFC/NIST | ✅ hashlib | 6 | ✅ |
| SHA3_256 | ✅ RFC/NIST | ✅ hashlib | 6 | ✅ |
| SHA3_512 | ✅ RFC/NIST | ✅ hashlib | 6 | ✅ |
| RIPEMD160 | ✅ RFC/NIST | ✅ hashlib | 6 | ✅ |
| HMAC-SHA1 | ✅ RFC | ✅ hmac | 4 | ✅ |
| HMAC-SHA256 | ✅ RFC | ✅ hmac | 4 | ✅ |
| PBKDF2-HMAC-SHA256 | ✅ RFC | ✅ cryptography | 27 | ✅ |
| RSA-OAEP/PSS | ✅ RFC 8017 | ✅ cryptography | 2 | ✅ |
| RSA-PKCS1-v1_5 | ✅ RFC 8017 | ✅ cryptography | 2 | ✅ |
| ECDSA secp160r1 | ✅ RFC 6979 | ❌ N/A | 1 | ✅ KAT-only |
| Base64 | ✅ RFC 4648 | ✅ python base64 | 12 | ✅ |
| UTF-8 | ✅ Unicode | ✅ Python codec | 13 | ✅ |

Notes:
- RC6 is KAT-only because mainstream Python cryptography libraries do not ship RC6.
- ECDSA secp160r1 is KAT-only because cryptography does not expose secp160r1.
- RSA PKCS#1 v1.5 uses the Rust core FFI directly; the HTTP layer intentionally exposes OAEP/PSS only.

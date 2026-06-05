"""Bridge for hash / HMAC / PBKDF2 to the Rust core."""

from __future__ import annotations

from app.schemas.hash import HashRequest, HashResult, HmacRequest, Pbkdf2Request


async def hash_(_algo: str, _req: HashRequest) -> HashResult:
    raise NotImplementedError("dispatch to cryptolab_core.{sha1,sha256,...} → time → return")


async def hmac(_algo: str, _req: HmacRequest) -> HashResult:
    raise NotImplementedError("cryptolab_core.hmac_{sha1,sha256}")


async def pbkdf2(_req: Pbkdf2Request) -> HashResult:
    raise NotImplementedError("reject iterations < 100_000; call cryptolab_core.pbkdf2_hmac_sha256")

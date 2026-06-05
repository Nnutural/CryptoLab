"""Tests for /api/v1/hash/* (SHA-1/2/3, RIPEMD, HMAC, PBKDF2)."""

import pytest


@pytest.mark.skip(reason="init stage")
async def test_sha256_rfc_vector():
    raise NotImplementedError

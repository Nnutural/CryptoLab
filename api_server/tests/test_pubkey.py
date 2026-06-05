"""Tests for /api/v1/pubkey/* (RSA / ECC / ECDSA)."""

import pytest


@pytest.mark.skip(reason="init stage")
async def test_rsa_oaep_roundtrip():
    raise NotImplementedError


@pytest.mark.skip(reason="init stage")
async def test_ecdsa_rfc6979_kat():
    raise NotImplementedError

"""Tests for /api/v1/symmetric/* (AES / SM4 / RC6)."""

import pytest


@pytest.mark.skip(reason="init stage")
async def test_aes_gcm_roundtrip():
    raise NotImplementedError

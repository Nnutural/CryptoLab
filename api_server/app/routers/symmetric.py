"""Symmetric encryption endpoints: AES / SM4 / RC6 — key_id based."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Path, Request
from sqlalchemy.orm import Session

from app.core.exceptions import CryptoAPIException
from app.core.status_codes import DEFAULT_MESSAGES, StatusCode
from app.db.session import get_db
from app.middleware.auth import get_current_user
from app.schemas.common import APIResponse
from app.schemas.keys import SymmetricKeygenRequest
from app.schemas.symmetric import (
    SymmetricDecryptRequest,
    SymmetricDecryptResponse,
    SymmetricEncryptRequest,
    SymmetricEncryptResponse,
)
from app.services import symmetric_service

router = APIRouter()
USER_DEP = Depends(get_current_user)
DB_DEP = Depends(get_db)

ALGO = Path(..., pattern="^(aes|sm4|rc6)$", description="Algorithm name")


@router.post("/keygen", response_model=APIResponse[dict])
async def keygen(
    request: Request,
    req: SymmetricKeygenRequest,
    user=USER_DEP,
    db: Session = DB_DEP,
) -> APIResponse[dict]:
    """Generate a random symmetric key and store it."""
    key_id = await symmetric_service.keygen(db, user, req)
    return _ok(request, {"key_id": key_id, "algorithm": req.algorithm, "key_type": "symmetric"})


@router.post("/{algo}/encrypt", response_model=APIResponse[SymmetricEncryptResponse])
async def encrypt(
    request: Request,
    req: SymmetricEncryptRequest,
    algo: str = ALGO,
    user=USER_DEP,
    db: Session = DB_DEP,
) -> APIResponse[SymmetricEncryptResponse]:
    """Encrypt plaintext with the chosen algorithm + mode + padding."""
    if req.verbose:
        _validate_verbose_request(algo, req)
        result = await symmetric_service.aes_encrypt_with_trace_op(db, user, algo, req)
    else:
        result = await symmetric_service.encrypt(db, user, algo, req)
    return _ok(request, result)


@router.post("/{algo}/decrypt", response_model=APIResponse[SymmetricDecryptResponse])
async def decrypt(
    request: Request,
    req: SymmetricDecryptRequest,
    algo: str = ALGO,
    user=USER_DEP,
    db: Session = DB_DEP,
) -> APIResponse[SymmetricDecryptResponse]:
    """Decrypt ciphertext."""
    result = await symmetric_service.decrypt(db, user, algo, req)
    return _ok(request, result)


def _ok(request: Request, data: object) -> APIResponse:
    return APIResponse(
        code=StatusCode.OK,
        message=DEFAULT_MESSAGES[StatusCode.OK],
        data=data,
        trace_id=getattr(request.state, "trace_id", "00000000-0000-0000-0000-000000000000"),
    )


def _validate_verbose_request(algo: str, req: SymmetricEncryptRequest) -> None:
    if algo != "aes" or req.algorithm != "aes":
        raise CryptoAPIException(
            StatusCode.ALGORITHM_UNSUPPORTED,
            "verbose mode is only supported for AES",
        )
    if req.mode != "ECB":
        raise CryptoAPIException(StatusCode.PARAM_MISSING, "verbose mode requires ECB mode")
    try:
        plaintext = req.plaintext_bytes()
    except ValueError as exc:
        raise CryptoAPIException(StatusCode.ENCODING_ERROR, str(exc)) from exc
    if len(plaintext) != 16:
        raise CryptoAPIException(
            StatusCode.PARAM_MISSING,
            "verbose mode requires exactly 16 bytes plaintext",
        )

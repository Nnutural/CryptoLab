"""Auth DTOs."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=64)
    password: str = Field(..., min_length=8, max_length=128)


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int


class RegisterResponse(BaseModel):
    user_id: int
    created_at: datetime


class CurrentUserResponse(BaseModel):
    user_id: int
    username: str
    role: str
    created_at: datetime
    last_login_at: datetime | None

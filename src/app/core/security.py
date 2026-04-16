# src/app/core/security.py
"""
Security and auth utilities: password hashing + JWT token management.

Bcrypt
------
Uses passlib's CryptContext wrapper around bcrypt (cost factor 12).
Never call bcrypt directly — always go through the helpers below.

JWT
---
Access tokens are short-lived JWTs signed with ``settings.SECRET_KEY``.
Refresh tokens are opaque UUIDs stored in Redis (handled in AuthService).
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings
from app.exceptions import UnauthorizedError

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
ALGORITHM = "HS256"

# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Return True if the plain password matches the stored bcrypt hash."""
    return bool(_pwd_context.verify(plain_password, hashed_password))


def get_password_hash(password: str) -> str:
    """Return a bcrypt hash of the given password (cost factor 12)."""
    return str(_pwd_context.hash(password))


# ---------------------------------------------------------------------------
# JWT
# ---------------------------------------------------------------------------


def create_access_token(
    subject: str,
    expires_delta: timedelta | None = None,
) -> str:
    """Encode a JWT access token.

    Parameters
    ----------
    subject:
        The ``sub`` claim — typically a user UUID as a string.
    expires_delta:
        Override the default expiry from ``settings.ACCESS_TOKEN_EXPIRE_MINUTES``.
    """
    expire = datetime.now(UTC) + (
        expires_delta
        if expires_delta is not None
        else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload: dict[str, Any] = {"sub": subject, "exp": expire, "iat": datetime.now(UTC)}
    return str(jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM))


def decode_access_token(token: str) -> str:
    """Decode a JWT access token and return the subject (user UUID as string).

    Raises
    ------
    UnauthorizedError
        If the token is expired, malformed, or missing the ``sub`` claim.
    """
    try:
        payload: dict[str, Any] = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as err:
        raise UnauthorizedError("Could not validate credentials") from err

    sub: str | None = payload.get("sub")
    if not sub:
        raise UnauthorizedError("Token missing subject claim")
    return sub

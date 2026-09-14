from uuid import UUID

import jwt
from pwdlib import PasswordHash
from pydantic import BaseModel, Field, FutureDatetime

ALGORITHM = "HS256"
password_hash = PasswordHash.recommended()


class TokenPayload(BaseModel):
    exp: FutureDatetime = Field()
    sub: UUID
    scopes: list[str] | None = None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return password_hash.hash(password)


def encode(payload: TokenPayload, secret: str) -> str:
    token_payload = {"sub": str(payload.sub), "exp": payload.exp}

    if payload.scopes:
        token_payload["scopes"] = payload.scopes

    return jwt.encode(payload=token_payload, key=secret, algorithm=ALGORITHM)


def decode(token: str, secret: str) -> TokenPayload:
    return TokenPayload.model_validate(
        jwt.decode(token, secret, algorithms=[ALGORITHM])
    )

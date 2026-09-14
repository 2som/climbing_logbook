from collections.abc import Awaitable, Callable
from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt
from pydantic import BaseModel

from features.users.users_repository import UsersRepository
from libraries.auth import TokenPayload, encode, decode, verify_password
from libraries.errors import UnauthenticatedError


SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24


class Token(BaseModel):
    access_token: str
    token_type: str


class AuthenticatedUser(BaseModel):
    uuid: UUID


class AuthService:
    def __init__(
        self,
        users_repository: UsersRepository,
        auth_secret_key: str,
        auth_expire_minutes: int,
    ):
        self._users_repository = users_repository
        self._auth_secret_key = auth_secret_key
        self._auth_expire_minutes = auth_expire_minutes
        
    async def login(self, email: str, password: str) -> Token:
        user = await self._users_repository.get_by_email(email)
        if not user:
            # verify anyway so the request response times are no different
            verify_password(password, "some-dummy-text")
            raise UnauthenticatedError("Invalid credentials")
        if not verify_password(password, user.password):
            raise UnauthenticatedError("Invalid credentials")

        return Token(
            access_token=encode(
                payload=TokenPayload(
                    sub=user.uuid,
                    exp=datetime.now(timezone.utc)
                    + timedelta(minutes=self._auth_expire_minutes),
                ),
                secret=self._auth_secret_key,
            ),
            token_type="bearer",
        )

    async def register():
        pass

    async def logout():
        pass


async def verify_user(
    token,
    auth_secret_key: str,
    auth_expire_minutes: int,
    resolver: Callable[[str], Awaitable[BaseModel]],
) -> AuthenticatedUser:
    try:
        payload = decode(token=token.credentials, secret=auth_secret_key)
        sub = payload.sub
        if sub is None:
            raise UnauthenticatedError("Invalid credentials")
        # TODO CHECK IS EXPIRED
    except jwt.InvalidTokenError:
        raise UnauthenticatedError("Invalid credentials")
    resolved_user = await resolver(sub)
    if resolved_user is None:
        raise UnauthenticatedError("Invalid credentials")
    return AuthenticatedUser.model_validate(resolved_user.model_dump())

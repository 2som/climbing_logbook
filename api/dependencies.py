from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPBearer

from api.settings import Settings
from features.auth import AuthenticatedUser, verify_user
from features.users import UsersRepository
from libraries.db.session import get_session
from sqlalchemy.ext.asyncio import AsyncSession


bearer_scheme = HTTPBearer(
    auto_error=False,
    scheme_name="BearerAuth",
    description="Access token issued by the identity provider (aiam.care).",
)


@lru_cache
def get_settings():
    return Settings()


def get_users_repository():
    return UsersRepository()


async def get_current_user(
    token: Annotated[str, Depends(bearer_scheme)],
    resolver: Annotated[UsersRepository, Depends(get_users_repository)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> AuthenticatedUser:
    return await verify_user(
        token,
        auth_secret_key=settings.auth_secret_key,
        resolver=resolver.get,
    )


CurrentUser = Annotated[AuthenticatedUser, Depends(get_current_user)]
DbSession = Annotated[AsyncSession, Depends(get_session)]
from typing import Annotated

from fastapi import Depends

from api.dependencies import DbSession, get_settings
from api.settings import Settings
from features.auth import AuthService
from features.users import UsersRepository


def get_auth_service(session: DbSession, settings: Annotated[Settings, Depends(get_settings)]):
    repository = UsersRepository(session)
    return AuthService(repository, auth_secret_key=settings.auth_secret_key, auth_expire_minutes=settings.access_token_expire_minutes)
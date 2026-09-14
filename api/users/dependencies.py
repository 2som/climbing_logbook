from typing import Annotated
from fastapi import Depends

from api.dependencies import get_users_repository
from features.users import UsersRepository, UsersService


def get_users_service(
    repository: Annotated[UsersRepository, Depends(get_users_repository)],
):
    return UsersService(repository)

from uuid import UUID

from features.users.users_repository import User, UsersRepository


class UsersService:
    def __init__(self, repository: UsersRepository):
        self._repository = repository

    async def get(self, uuid: UUID) -> User | None:
        return await self._repository.get(uuid)


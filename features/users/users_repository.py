from uuid import UUID

from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from features.users.model import UserModel


class User(BaseModel):
    uuid: UUID
    email: str
    disabled: bool
    password: str = Field(exclude=True)


class UsersRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get(self, uuid: UUID) -> User | None:
        result = (await self._session.execute(
            select(UserModel).where(UserModel.uuid == uuid)
        )).scalar_one_or_none()
        if not result:
            return None
        return User.model_validate(result.as_dict())

    async def get_by_email(self, email: str) -> User | None:
        result = (await self._session.execute(
            select(UserModel).where(UserModel.email == email)
        )).scalar_one_or_none()
        if not result:
            return None
        return User.model_validate(result.as_dict())

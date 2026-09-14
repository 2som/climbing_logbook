

from uuid import UUID

from pydantic import BaseModel, Field


fake_users_db = {
    "user@gmail.com": {
        "uuid": "9ae3b653-94c4-4848-993d-8675dc306272",
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "user@gmail.com",
        "password": "$argon2id$v=19$m=65536,t=3,p=4$Lubt8H8GmbHz+Fsg33bUEQ$Uffny4/6dTuH1fGYXsruVJJ4GscEORg3n9nhgOI4B/g",
        "disabled": False,
    },
}

class User(BaseModel):
    uuid: UUID
    username: str
    email: str
    disabled: bool
    password: str = Field(exclude=True)


class UsersRepository:
    async def get(self, uuid: UUID) -> User | None:
        for _, v in fake_users_db.items():
            if v["uuid"] == str(uuid):
                return User.model_validate(v)
        return None

    async def get_by_email(self, email: str) -> User | None:
        for _, v in fake_users_db.items():
            if v["email"] == email:
                return User.model_validate(v)
        return None

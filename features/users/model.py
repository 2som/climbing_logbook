from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column
from uuid_extensions import uuid7

from libraries.db.session import Base


class UserModel(Base):
    __tablename__ = "users"
    uuid: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    disabled: Mapped[bool]

    def as_dict(self) -> dict:
        return {
            "uuid": self.uuid,
            "email": self.email,
            "password": self.password,
            "disabled": self.disabled,
        }

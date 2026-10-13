from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column
from uuid_extensions import uuid7
from sqlalchemy import UniqueConstraint
from libraries.db.session import Base


class TrainingPlan(Base):
    __tablename__ = "training_plans"
    __table_args__ = (UniqueConstraint("name", "user_uuid"),)
    uuid: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)
    name: Mapped[str]
    user_uuid: Mapped[UUID]

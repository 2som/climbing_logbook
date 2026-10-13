from uuid import UUID

from sqlalchemy import JSON, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from libraries.db.session import Base
from uuid_extensions import uuid7



class PlannedSession(Base):
    __tablename__ = "planned_sessions"
    uuid: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)
    user_uuid: Mapped[UUID] = mapped_column(ForeignKey("users.uuid"))
    plan_uuid: Mapped[UUID | None] = mapped_column(ForeignKey("training_plans.uuid"), nullable=True)
    session_uuid: Mapped[UUID] = mapped_column(ForeignKey("sessions.uuid"))
    finished: Mapped[bool] = mapped_column(default=False)
    duration_minutes: Mapped[int | None] = mapped_column(default=None)
    notes: Mapped[str | None] = mapped_column(default=None)
    start_date: Mapped[Date] = mapped_column(Date)

    excercies: Mapped[list["PlannedExcercise"]] = relationship()

class PlannedExcercise(Base):
    __tablename__ = "planned_excercies"    
    uuid: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)
    planned_sesssion_uuid: Mapped[UUID] = mapped_column(ForeignKey("planned_sessions.uuid"))
    excercise_uuid: Mapped[UUID] = mapped_column(ForeignKey("excercises.uuid"))
    feedback: Mapped[dict | None] = mapped_column(JSON, nullable=True)


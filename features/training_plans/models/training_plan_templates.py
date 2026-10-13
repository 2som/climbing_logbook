from uuid import UUID

from uuid_extensions import uuid7
from sqlalchemy.orm import Mapped, mapped_column
from libraries.db.session import Base
from features.training_plans.models.enum import ExerciseUnitEnum

class ExerciseTemplate(Base):
    __tablename__ = "exercise_templates"
    uuid: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)
    name: Mapped[str]
    description: Mapped[str]
    feedback_enabled: Mapped[bool]
    sets: Mapped[int | None] = mapped_column(default=None)
    repetitions: Mapped[int | None] = mapped_column(default=None)
    duration_seconds: Mapped[int | None] = mapped_column(default=None)
    unit: Mapped[ExerciseUnitEnum | None] = mapped_column(default=None)
    unit_label: Mapped[str | None] = mapped_column(default=None)

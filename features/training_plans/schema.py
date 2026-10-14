import datetime
from typing import Self
from uuid import UUID

from pydantic import BaseModel

from features.training_plans.models.training_plan import Exercise, Phase, Session, TrainingPlan


class ExerciseResource(BaseModel):
    uuid: UUID
    session_uuid: UUID
    name: str
    description: str
    order: int

    @classmethod
    def from_model(cls, model: Exercise) -> Self:
        return cls(
            uuid=model.uuid,
            session_uuid=model.session_uuid,
            name=model.name,
            description=model.description,
            order=model.order,
        )


class SessionResource(BaseModel):
    uuid: UUID
    phase_uuid: UUID
    name: str
    description: str | None
    duration_minutes: int

    exercises: list[ExerciseResource]

    @classmethod
    def from_model(cls, model: Session) -> Self:
        return cls(
            uuid=model.uuid,
            phase_uuid=model.phase_uuid,
            name=model.name,
            description=model.description,
            duration_minutes=model.duration_minutes,
            exercises=[ExerciseResource.from_model(exercise) for exercise in model.excercises],
        )


class PhaseResource(BaseModel):
    uuid: UUID
    name: str
    description: str
    start_at: datetime.date | None
    end_at: datetime.date | None
    active: bool
    order: int
    duration_weeks: int

    sessions: list[SessionResource]

    @classmethod
    def from_model(cls, model: Phase, start_at: datetime.date | None = None) -> Self:
        end_at = start_at + datetime.timedelta(weeks=model.duration_weeks, days=-1) if start_at else None
        active = bool(start_at and end_at and start_at <= datetime.date.today() <= end_at)
        return cls(
            uuid=model.uuid,
            name=model.name,
            description=model.description,
            start_at=start_at,
            end_at=end_at,
            active=active,
            order=model.order,
            duration_weeks=model.duration_weeks,
            sessions=[SessionResource.from_model(session) for session in model.sessions],
        )


class TrainingPlanResource(BaseModel):
    uuid: UUID
    name: str
    phases: list[PhaseResource]

    @classmethod
    def from_model(cls, model: TrainingPlan, start_date: datetime.date | None = None) -> Self:
        """``start_date`` is the active plan's start; without it phases get no dates and are never active."""
        phases = []
        cursor = start_date
        for phase in model.phases:
            phases.append(PhaseResource.from_model(phase, cursor))
            if cursor:
                cursor += datetime.timedelta(weeks=phase.duration_weeks)
        return cls(uuid=model.uuid, name=model.name, phases=phases)

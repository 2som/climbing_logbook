from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

class TrainingPlan:
    uuid: UUID
    name: str #unique

class Phase:
    uuid: UUID
    name: str
    order: int
    duration_weeks: int

class TrainingPlanPhases:
    phase_uuid: UUID
    plan_uuid: UUID

class PhasesSessions:
    session_uuid: UUID
    phase_uuid: UUID

class Session:
    uuid: UUID
    name: str
    description: str

class Excercise:
    uuid: UUID
    name: str
    description: str
    feedback_enabled: bool
    sets: int | None
    repetitions: int | None
    duration_seconds: int | None
    unit: Literal["kg", "seconds"]
    unit_label: dict #{ "kg": "weight", "seconds": "duration"}

class SessionExcercies:
    session_uuid: UUID
    excercise_uuid: UUID

def create_plan(name: str):
    return TrainingPlan(name)


class UserSession:
    date: datetime
    status: Literal["planned", "done"]
    created_at: datetime
    session_uuid: UUID
    training_plan_uuid: UUID | None
    duration_minutes: int | None
    note: str | None
    perceived_difficulty: int | None
    excercies: list #of UserExcercies - raczej nie model tylko JSON

class UserExcercies:
    user_session_uuid: UUID
    excercise_data: dict | None # { "set1": { "repetitions": 5, "weight": 75 } }
    note: str | None

"""
training-plans

GET /training-plans

POST /training-plans

PATCH /training-plans/{plan_uuid}

"""



"""
GET /user-sessions

POST /user-sessions

PATCH /user-sessions/{session_uuid}

DELETE /user-sessions/{session_uuid}

"""
import datetime
from typing import Annotated, Self
from uuid import UUID

from fastapi import APIRouter, Query
from pydantic import BaseModel, model_validator

from api.dependencies import CurrentUser, DbSession
from features.calendar.calendar import index_planned_sessions, plan_session
from features.training_plans.training_plans_service import get_training_session


router = APIRouter(prefix="/calendar", tags=["calendar"])


class PlanSessionRequest(BaseModel):
    session_uuid: UUID
    start_date: datetime.date


class IndexCalendarQuery(BaseModel):
    start_date: datetime.date
    end_date: datetime.date

    @model_validator(mode="after")
    def validate_dates(self) -> Self:
        if self.end_date <= self.start_date:
            raise ValueError("End date must be greater than the start date.")
        return self


@router.post("")
async def plan(request: PlanSessionRequest, user: CurrentUser, db_session: DbSession):
    training_session = await get_training_session(
        user_uuid=user.uuid, session_uuid=request.session_uuid, db_session=db_session
    )
    if not training_session:
        raise Exception(f"Session with {request.session_uuid} not found")
    await plan_session(
        user_uuid=user.uuid,
        training_session=training_session,
        date=request.start_date,
        db_session=db_session,
    )


@router.get("")
async def index(
    query: Annotated[IndexCalendarQuery, Query()],
    user: CurrentUser,
    db_session: DbSession,
):
    return await index_planned_sessions(
        user_uuid=user.uuid,
        start_date=query.start_date,
        end_date=query.end_date,
        db_session=db_session,
    )

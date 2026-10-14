import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from features.calendar.model import PlannedExercise, PlannedSession
from features.training_plans.models.training_plan import Session


async def plan_session(
    user_uuid: UUID,
    training_session: Session,
    date: datetime.date,
    db_session: AsyncSession,
):
    planned_session = PlannedSession(
        user_uuid=user_uuid,
        plan_uuid=training_session.plan_uuid,
        session_uuid=training_session.uuid,
        start_date=date,
    )
    planned_session_excercises = [
        PlannedExercise(
            planned_session_uuid=planned_session.uuid, exercise_uuid=excercise.uuid
        )
        for excercise in training_session.excercises
    ]

    planned_session.exercises = planned_session_excercises
    db_session.add(planned_session)
    await db_session.commit()

    return planned_session


async def index_planned_sessions(
    user_uuid: UUID,
    start_date: datetime.date,
    end_date: datetime.date,
    db_session: AsyncSession,
):
    planned_sessions = await db_session.execute(
        select(PlannedSession)
        .where(
            PlannedSession.user_uuid == user_uuid,
            PlannedSession.start_date >= start_date,
            PlannedSession.start_date <= end_date,
        )
        .options(selectinload(PlannedSession.exercises))
    )

    return list(planned_sessions.scalars())

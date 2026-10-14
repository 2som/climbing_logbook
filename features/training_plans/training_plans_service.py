from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from features.training_plans.models.training_plan import (
    ActiveTrainingPlan,
    Phase,
    Session,
    TrainingPlan,
)
from features.training_plans.schema import TrainingPlanResource

async def get_active_training_plan_for_user(user_uuid: UUID, session: AsyncSession):
    active = (
        await session.execute(
            select(ActiveTrainingPlan).where(ActiveTrainingPlan.user_uuid == user_uuid)
        )
    ).scalar_one_or_none()

    if not active:
        return None

    plan = (
        await session.execute(
            select(TrainingPlan)
            .where(TrainingPlan.uuid == active.plan_uuid)
            .options(
                selectinload(TrainingPlan.phases)
                .selectinload(Phase.sessions)
                .selectinload(Session.excercises)
            )
            .join(ActiveTrainingPlan, ActiveTrainingPlan.plan_uuid == TrainingPlan.uuid)
            .where(ActiveTrainingPlan.user_uuid == user_uuid)
        )
    ).scalar_one_or_none()

    return TrainingPlanResource.from_model(plan, active.start_date) if plan else None

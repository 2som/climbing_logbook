from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from features.training_plans.models.training_plan import TrainingPlan



async def create_training_plan(name: str, user_uuid: UUID, session: AsyncSession):
    training_plan = TrainingPlan(name=name, user_uuid=user_uuid)
    session.add(training_plan)
    await session.flush()
    await session.commit()
    return training_plan

async def get_owned_training_plans(user_uuid: UUID, session: AsyncSession):
    result = await session.execute(select(TrainingPlan).where(TrainingPlan.user_uuid == user_uuid))
    return list(result.scalars())

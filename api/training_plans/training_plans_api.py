from fastapi import APIRouter
from pydantic import BaseModel

from api.dependencies import CurrentUser, DbSession
from features.training_plans.training_plans_service import (
    get_active_training_plan_for_user,
)


router = APIRouter(prefix="/training-plans", tags=["training_plans"])


class StoreTrainingPlanRequest(BaseModel):
    name: str


@router.get("/training-plans/active")
async def get_current(user: CurrentUser, session: DbSession):
    return await get_active_training_plan_for_user(user.uuid, session)

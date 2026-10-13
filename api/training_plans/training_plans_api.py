from typing import Annotated
from uuid import UUID

from fastapi import APIRouter
from pydantic import BaseModel

from api.dependencies import CurrentUser, DbSession
from features.training_plans.training_plans_service import create_training_plan, get_owned_training_plans


router = APIRouter(
    prefix="/training-plans",
    tags=["training_plans"]
)


class StoreTrainingPlanRequest(BaseModel):
    name: str

@router.post("/training-plans")
async def store(request: StoreTrainingPlanRequest, user: CurrentUser, session: DbSession):
    plan = await create_training_plan(request.name, user.uuid, session)
    return plan

@router.get("/training-plans")
async def index(user: CurrentUser, session: DbSession):
    return await get_owned_training_plans(user.uuid, session)

@router.get("/training-plans/current")
async def get_current():
    pass

@router.get("/training-plans/{plan_uuid}")
async def get():
    pass

@router.patch("/training-plans/{plan_uuid}")
async def edit():
    pass


@router.put("/training-plans/{plan_uuid}/phases")
async def update_training_plan_phases(list):
    pass
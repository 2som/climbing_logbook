from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from api.auth.dependencies import get_auth_service
from api.dependencies import CurrentUser
from api.users.dependencies import get_users_service
from features.auth import AuthService, Token
from features.users import UsersService

router = APIRouter(prefix="/auth", tags=["auth"])

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
async def login(
    request: LoginRequest,
    service: Annotated[AuthService, Depends(get_auth_service)]
) -> Token:
    return await service.login(request.email, request.password)
    
@router.get("/user")
async def me(current_user: CurrentUser, service: Annotated[UsersService, Depends(get_users_service)]):
    return await service.get(current_user.uuid)

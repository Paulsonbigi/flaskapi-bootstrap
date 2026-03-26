from typing import Annotated
from fastapi import APIRouter, Depends
from app.services import UserService
from app.schemas import UserResponse
from app.dependencies import get_current_user_id, get_user_service

router = APIRouter(dependencies=[Depends(get_current_user_id)])

@router.get(
    "/me",
    response_model=UserResponse,
    summary="User profile",
)
async def get_me(
    user_id: Annotated[int, Depends(get_current_user_id)],
    service: Annotated[UserService, Depends(get_user_service)],
):
    return await service.me(user_id=user_id)
from fastapi import APIRouter, Depends
from app.services.user import UserService
from app.dependencies import get_current_user_id, get_user_service

router = APIRouter()

userService = Depends(get_user_service)
user_id = Depends(get_current_user_id)

@router.get(
    "/me",
    # response_model=TokenResponse,
    summary="User profile",
)
def get_me(
    user_id: int = user_id,
    service: UserService = userService,
):
    return service.get_by_id(user_id)
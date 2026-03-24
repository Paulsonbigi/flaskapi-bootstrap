from fastapi import APIRouter, Depends, status, UploadFile, File

from app.schemas import LoginUser, RegisterUser, LoginResponse
from app.services import UserService
from app.dependencies import get_user_service

router = APIRouter()

@router.post(
    "/register",
    # response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register(
    payload: RegisterUser,
    service: UserService = Depends(get_user_service),
):
    return service.register(payload)


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Login and receive access token",
)
async def login(
    payload: LoginUser,
    service: UserService = Depends(get_user_service),
):
    return service.login(payload)
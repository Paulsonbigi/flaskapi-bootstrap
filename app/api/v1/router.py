from fastapi import APIRouter
from app.api.v1.auth_router import router as auth_router
from app.api.v1.user_router import router as user_router
from app.api.v1.question_router import router as question_router
from app.api.v1.choice_router import router as choice_router

router = APIRouter()
router.include_router(auth_router, prefix="/auth", tags=["Auth"])
router.include_router(user_router, prefix="/users", tags=["USER"])
router.include_router(choice_router, prefix="/choices", tags=["CHOICES"])
router.include_router(question_router, prefix="/questions", tags=["QUESTIONS"])

from fastapi import APIRouter, Depends
from app.services import QuestionService
from app.dependencies import get_current_user_id, get_question_service, get_user_service

router = APIRouter(dependencies=[Depends(get_current_user_id)])

@router.get(
    "",
    # response_model=TokenResponse,
    summary="Fetch questions",
)
def get_questions(
    service: QuestionService = Depends(get_question_service),
):
    return service.get_questions()
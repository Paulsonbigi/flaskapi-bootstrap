from fastapi import APIRouter, Depends
from app.services import QuestionService
from app.schemas import QuestionFilterParams
from app.dependencies import get_question_filters, get_current_user_id, get_question_service

router = APIRouter(dependencies=[Depends(get_current_user_id)])

@router.get(
    "",
    # response_model=TokenResponse,
    summary="Fetch questions",
)
def get_questions(
    filters: QuestionFilterParams = Depends(get_question_filters),
    service: QuestionService = Depends(get_question_service),
):
    return service.get_questions(filters = filters)
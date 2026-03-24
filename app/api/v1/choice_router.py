from fastapi import APIRouter, Depends
from app.dependencies import get_current_user_id, get_choice_service
from app.services import ChoiceService

router = APIRouter()

user_id = Depends(get_current_user_id)

@router.get(
    "/{question_id}",
    summary="Fetch questions",
)
def get_choices_by_question_id(
    question_id: int,
    service: ChoiceService = Depends(get_choice_service),
):
    return service.get_choices(question_id)
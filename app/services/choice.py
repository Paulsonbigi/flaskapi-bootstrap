from sqlalchemy.orm import Session
from app.models import Choices
from app.repository import ChoiceRepository
from app.exceptions import ErrorCode, AppException
from starlette import status

class ChoiceService:
    def __init__(self, db: Session):
        self.choice_repo = ChoiceRepository(db)

    def get_choices(self, question_id: int)-> list[Choices]:
        choices = self.choice_repo.find_all({ 'question_id': question_id })
        print(len(choices))
        if len(choices) == 0:
            raise AppException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Invalid question id: {question_id}",
                error_code= ErrorCode.QUESTION_NOT_FOUND,
            )
        return choices
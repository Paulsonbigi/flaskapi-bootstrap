from sqlalchemy.orm import Session
from app.models import Choices
from app.repository import ChoiceRepository, QuestionRepository
from app.schemas import ChoiceBase


class ChoiceService:
    def __init__(self, db: Session):
        self.choice_repo = ChoiceRepository(db)

    def get_choices(self, question_id: int)-> list[Choices]:
        choices = self.choice_repo.find_all({ 'question_id': question_id })
        return choices
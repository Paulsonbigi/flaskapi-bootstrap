
from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.general import HelperService
from app.database import get_db
from app.services import ChoiceService, QuestionService, UserService

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)

def get_question_service(db: Session = Depends(get_db))-> QuestionService:
    return QuestionService(db)

def get_choice_service(db: Session = Depends(get_db)) -> ChoiceService:
    return ChoiceService(db)

def get_helper_service() -> HelperService:
    return HelperService()

def get_current_user_id(
    token: str,
    helper: HelperService = Depends(get_helper_service),
) -> int:
    return helper.decode_token(token)

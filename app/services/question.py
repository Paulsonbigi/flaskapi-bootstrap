from sqlalchemy.orm import Session
from starlette import status
from app.exceptions import AppException, ErrorCode
from app.models import Choices, Questions
from app.repository import ChoiceRepository, QuestionRepository
from app.schemas import ChoiceBase, QuestionFilterParams

class QuestionService:
    def __init__(self, db: Session):
        self.question_repo = QuestionRepository(db)
        self.choice_repo = ChoiceRepository(db)
        self.db = db

    def create(self, payload: ChoiceBase):
        try:
            db_question = self.question_repo.create(question_text=payload.question_text)

            for choice in payload.choices:
                db_choice = Choices(
                    choice_text=choice.choice_text,
                    is_correct=choice.is_correct,
                    question_id=db_question.id,
                )
                self.choice_repo.save(db_choice)

            self.db.commit()
            self.db.refresh(db_question)
            return db_question

        except Exception as e:
            self.db.rollback()
            raise e
    
    def get_questions(self, filters: QuestionFilterParams) -> dict:
        return self.question_repo.paginate(
            **filters.to_paginate_kwargs(search_fields=["question_text"]),
            filters=filters.get_filters(),
        )
    
    def get_question_by_id(self, question_id: int)-> Questions:
        question = self.question_repo.find_by_id(question_id)
        if question is None:
            raise AppException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found",
                error_code= ErrorCode.QUESTION_NOT_FOUND,
            )
        return question
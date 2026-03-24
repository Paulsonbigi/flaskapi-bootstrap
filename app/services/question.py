from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models import Choices, Questions
from app.repository import ChoiceRepository, QuestionRepository
from app.schemas import ChoiceBase

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
    
    def get_questions(self):
        db_questions = self.question_repo.find_all()
        return db_questions
    
    def get_question_by_id(self, question_id: int)-> Questions:
        question = self.question_repo.find_by_id(question_id)
        if question is None:
            raise HTTPException(status_code=404, detail='Question not found')
        return question
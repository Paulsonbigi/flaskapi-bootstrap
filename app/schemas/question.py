from typing import List, Optional
from pydantic import BaseModel
from app.schemas import ChoiceBase, PaginationParams

class QuestionBase(BaseModel):
    question_text: str
    choices: List[ChoiceBase]

class QuestionFilterParams(PaginationParams):
    question_text: Optional[str] = None

    def get_filters(self) -> dict:
        """Returns only non-None exact match filters"""
        return {
            k: v for k, v in {
                "question_text": self.question_text,
            }.items() if v is not None
        }
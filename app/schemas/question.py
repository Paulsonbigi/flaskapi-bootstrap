from typing import List
from pydantic import BaseModel
from app.schemas import ChoiceBase


class QuestionBase(BaseModel):
    question_text: str
    choices: List[ChoiceBase]
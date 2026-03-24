from app.database import SessionLocal
from app.models import Questions
from app.repository import BaseRepository


class QuestionRepository(BaseRepository[Questions]):
    def __init__(self, db: SessionLocal):
        super().__init__(Questions, db)
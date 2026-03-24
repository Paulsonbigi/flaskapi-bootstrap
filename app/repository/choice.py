from app.database import SessionLocal
from app.models import Choices
from app.repository import BaseRepository


class ChoiceRepository(BaseRepository[Choices]):
    def __init__(self, db: SessionLocal):
        super().__init__(Choices, db)
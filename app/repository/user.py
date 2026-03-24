from app.database import SessionLocal
from app.models import Users
from app.repository import BaseRepository


class UserRepository(BaseRepository[Users]):
    def __init__(self, db: SessionLocal):
        super().__init__(Users, db)

    def find_by_email(self, email: str) -> Users | None:
        return self.find_one(email=email)
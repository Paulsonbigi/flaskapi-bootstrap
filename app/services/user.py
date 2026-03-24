from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.core import HelperService
from app.models import Users
from app.repository import UserRepository
from app.schemas.user import RegisterUser
   
#  helper: HelperService = Depends(get_helper_service),


class UserService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)
        self.helper_service = HelperService()
        self.db = db

    def register(self, payload: RegisterUser):
        email_exists = self.user_repo.find_one(email=payload.email)
        if email_exists:
            raise HTTPException(status_code=409, detail="Account already exists")

        hashed_password = self.helper_service.password_hash(password=payload.password)

        user = self.user_repo.create(
            email=payload.email,
            first_name=payload.first_name,
            last_name=payload.last_name,
            password=hashed_password,
        )
        self.db.commit()
        self.db.refresh(user)
        return user

    def login(self, payload: RegisterUser):
        pass

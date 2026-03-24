from sqlalchemy.orm import Session
from starlette import status
from app.core import HelperService
from app.exceptions import ErrorCode, AppException
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
            raise AppException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Account already exists",
                error_code= ErrorCode.EMAIL_ALREADY_EXISTS,
            )

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
        account = self.user_repo.find_one(email=payload.email)
        if account is None:
            raise AppException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Invalid email and password",
                error_code= ErrorCode.EMAIL_ALREADY_EXISTS,
            )
        pass

from sqlalchemy.orm import Session
from starlette import status
from app.core import HelperService
from app.exceptions import ErrorCode, AppException
from app.repository import UserRepository
from app.schemas import RegisterUser, LoginResponse, UserResponse
import logging

from app.sources import source_registry

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)
        self.helper_service = HelperService()
        self.registry = source_registry
        self.db = db

    def register(self, payload: RegisterUser):
        logger.info(f"account registration begins for ${payload.email}")
        email_exists = self.user_repo.find_one(email=payload.email)
        if email_exists:
            raise AppException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Account already exists",
                error_code= ErrorCode.EMAIL_ALREADY_EXISTS,
            )

        hashed_password = self.helper_service.password_hash(password=payload.password)

        user = self.user_repo.create(
            email=payload.email.lower(),
            first_name=payload.first_name,
            last_name=payload.last_name,
            password=hashed_password,
        )
        self.db.commit()
        self.db.refresh(user)
        logger.info(f"account registration successful for ${payload.email}")

        return { "message": 'Account creation successful' }

    def login(self, payload: RegisterUser) -> LoginResponse:
        logger.info(f"account login begins for ${payload.email}")

        user = self.user_repo.find_one(email=payload.email.lower())
        print(user, payload.email)
        if user is None:
            raise AppException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Invalid email and password",
                error_code= ErrorCode.EMAIL_ALREADY_EXISTS,
            )
        verify_password = self.helper_service.verify_password(
            plain = payload.password, 
            hashed = user.password
        )
        if not verify_password:
            raise AppException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Invalid  and password",
                error_code= ErrorCode.EMAIL_ALREADY_EXISTS,
            )
        access_token = self.helper_service.create_access_token(user_id = user.id)
        logger.info(f"account login successful for ${payload.email}")
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user,
        }


    def me(self, user_id: int) -> UserResponse:
        user = self.user_repo.find_by_id(user_id)

        if user is None:
            raise AppException(...)

        logger.info("account profile retrieved successfully for %s", user_id)

        return user

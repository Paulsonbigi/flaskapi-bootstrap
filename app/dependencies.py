
from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.general import HelperService
from app.database import get_db
from app.services import ChoiceService, QuestionService, UserService
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.exceptions import ErrorCode, AppException
from starlette import status

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/login", auto_error=False)
security = HTTPBearer(auto_error=False)

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)

def get_question_service(db: Session = Depends(get_db))-> QuestionService:
    return QuestionService(db)

def get_choice_service(db: Session = Depends(get_db)) -> ChoiceService:
    return ChoiceService(db)

def get_helper_service() -> HelperService:
    return HelperService()

def get_current_user_id(
    token: str | None = Depends(security),
    helper: HelperService = Depends(get_helper_service),
) -> int:
    if not token:
        raise AppException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            error_code=ErrorCode.INVALID_TOKEN,
        )
    return helper.decode_token(token)

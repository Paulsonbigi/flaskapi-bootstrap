
from fastapi import Depends, Query
from sqlalchemy.orm import Session
from app.config import Settings, get_settings
from app.core import HelperService
from app.database import get_db
from app.schemas import PaginationParams, QuestionFilterParams
from app.services import ChoiceService, QuestionService, UserService
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.exceptions import ErrorCode, AppException
from starlette import status

from app.sources.alpha_vantage import AlphaVantageSource

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

def get_pagination(
    page:      int = Query(default=1,     ge=1),
    page_size: int = Query(default=10,    ge=1, le=100),
    order_by:  str = Query(default=None),
    search:  str = Query(default=None),
    order_dir: str = Query(default="asc", pattern="^(asc|desc)$"),
) -> PaginationParams:
    return PaginationParams(
        page=page,
        page_size=page_size,
        order_by=order_by,
        order_dir=order_dir,
        search=search,
    )

def get_question_filters(
    pagination:    PaginationParams = Depends(get_pagination),
    question_text: str = Query(default=None),
) -> QuestionFilterParams:
    return QuestionFilterParams(
        **pagination.model_dump(),
        question_text=question_text,
    )

def get_alpha_vantage_source(
    settings: Settings = Depends(get_settings)
):
    return AlphaVantageSource(settings=settings)
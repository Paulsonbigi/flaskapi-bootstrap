import bcrypt
from fastapi import status
from datetime import datetime, timezone, timedelta
from jose import jwt, JWTError
from app.config import get_settings
from app.exceptions import ErrorCode, AppException

settings = get_settings()

SECRET_KEY           = settings.secret_key
ALGORITHM            = "HS256"
TOKEN_EXPIRY_MINUTES = settings.access_token_expire_minutes

class HelperService:
    def __init__(self):
        # TODO document why this method is empty
        pass

    def password_hash(self, password: str) -> str:
        return bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

    def verify_password(self, plain: str, hashed: str) -> bool:
        return bcrypt.checkpw(
            plain.encode("utf-8"),
            hashed.encode("utf-8")
        )

    def create_access_token(self, user_id: int) -> str:
        payload = {
            "sub": str(user_id),
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRY_MINUTES),
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    def decode_token(self, token: str) -> int:
        try:
            payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("sub")
            if user_id is None:
                raise AppException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token",
                    error_code= ErrorCode.INVALID_TOKEN,
                )
            return int(user_id)
        except JWTError:
            raise AppException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                error_code= ErrorCode.INVALID_TOKEN,
            )
        
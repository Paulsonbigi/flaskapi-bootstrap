import bcrypt
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from jose import jwt, JWTError
from app.config import Settings

settings = Settings()

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
            "iat": datetime.now(datetime.timezone.utc),
            "exp": datetime.now(datetime.timezone.utc) + timedelta(minutes=TOKEN_EXPIRY_MINUTES),
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    def decode_token(self, token: str) -> int:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("sub")
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token",
                )
            return int(user_id)
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )
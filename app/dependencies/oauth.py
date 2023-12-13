from typing import Annotated
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from app.internal.helper.getenv import env

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


class LoggedInUser(BaseModel):
    user_id: str
    device_id: str
    is_admin: bool
    token_type: str


def get_user(user: dict):
    return LoggedInUser(
        user_id=user["user_id"],
        device_id=user["device_id"],
        is_admin=user["is_admin"],
        token_type=user["token_type"],
    )


async def verify_oauth(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        key = env("JWT_SECRET", "not-secure")
        user = jwt.decode(jwt=token, key=key, algorithms=["HS256"])
        return get_user(user)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid auth token"
        ) from exc

from typing import Annotated
from fastapi import Depends, Header, Request
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


async def verifyOAuth(request: Request, token: Annotated[str, Depends(oauth2_scheme)]):
    request.state.user = {"token": token}

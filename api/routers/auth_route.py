from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from prisma import Prisma
from api.dto.devices import Device
from api.dto.login_payload import LoginPayload
from api.dto.user import User

from api.services.auth_manager import AuthManager
from api.services.device_manager import DeviceManager
from api.services.user_manager import UserManager

router = APIRouter(prefix="/auth", tags=["users"])
prisma = Prisma()

deviceManager = DeviceManager(prisma)
userManager = UserManager(prisma)
authManager = AuthManager(userManager, deviceManager)


@router.post("/create")
async def create_user(user: User):
    return await authManager.register_user(user.email, user.password)


@router.post("/login")
async def user_login(login_data: LoginPayload):
    return await authManager.validate_login(login_data)


@router.post("/token")
async def open_api_login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    data = LoginPayload(
        email=form_data.username,
        password=form_data.password,
        device=Device(id=form_data.client_id, name="open-api-client"),
    )
    return await authManager.validate_login(data)

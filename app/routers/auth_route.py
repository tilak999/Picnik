from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.internal.schema.devices import Device
from app.internal.schema.login_payload import LoginPayload
from app.internal.schema.user import User
from app.internal.services.auth_manager import AuthManager
from app.internal.services.device_manager import DeviceManager
from app.internal.services.user_manager import UserManager
from prisma import Prisma

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
    if form_data.client_id is None:
        raise ValueError("device id is missing")
    data = LoginPayload(
        email=form_data.username,
        password=form_data.password,
        device=Device(id=form_data.client_id, name="open-api-client"),
    )
    return await authManager.validate_login(data)

from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
import jwt
import prisma
from pydantic import EmailStr
from hashlib import sha256
from api.dto.login_payload import LoginPayload
from api.helper.getenv import get_env
from api.services.device_manager import DeviceManager
from api.services.user_manager import UserManager


class AuthManager:
    """Authentication and authorisation management service"""

    def __init__(self, userManager: UserManager, deviceManager: DeviceManager) -> None:
        self.userManager = userManager
        self.deviceManager = deviceManager

    def generate_jwt(self, payload):
        return jwt.encode(payload=payload, key=get_env("JWT_KEY", "not-secure"))

    def generate_password_hash(self, password: str):
        return sha256(password.encode("UTF-8")).hexdigest()

    async def register_user(self, email: EmailStr, password: str):
        """Register new user"""
        password_hash = self.generate_password_hash(password)
        enableAdmin = True if await self.userManager.is_first_user() else False
        try:
            return await self.userManager.create_new_user(
                email, password_hash, enableAdmin
            )
        except prisma.errors.UniqueViolationError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email id already exist",
            )

    async def validate_login(self, login_data: LoginPayload):
        """Validate user login"""
        password_hash = self.generate_password_hash(login_data.password)
        user = await self.userManager.get_user(login_data.email, password_hash, True)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )
        authorised_device = await self.deviceManager.register_device_if_not_found(
            user.id, login_data.device
        )
        payload = {
            "user_id": user.id,
            "device_id": authorised_device.id,
            "is_admin": user.isSystemAdmin,
            "token_type": "bearer",
        }
        payload["access_token"] = self.generate_jwt(payload)
        return payload

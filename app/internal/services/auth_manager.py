from hashlib import sha256

import jwt
from fastapi import HTTPException, status
from pydantic import EmailStr

import prisma
from app.internal.helper.getenv import env
from app.internal.schema.login_payload import LoginPayload
from app.internal.services.device_manager import DeviceManager
from app.internal.services.user_manager import UserManager


class AuthManager:
    """Authentication and authorisation management service"""

    def __init__(
        self, user_manager: UserManager, device_manager: DeviceManager
    ) -> None:
        self.user_manager = user_manager
        self.device_manager = device_manager

    def generate_jwt(self, payload):
        return jwt.encode(payload=payload, key=env("JWT_SECRET", "not-secure"))

    def generate_password_hash(self, password: str):
        return sha256(password.encode("UTF-8")).hexdigest()

    async def register_user(self, email: EmailStr, password: str):
        """Register new user"""
        password_hash = self.generate_password_hash(password)
        enable_admin = bool(await self.user_manager.is_first_user())
        try:
            return await self.user_manager.create_new_user(
                email, password_hash, enable_admin
            )
        except prisma.errors.UniqueViolationError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email id already exist",
            ) from exc

    async def validate_login(self, login_data: LoginPayload):
        """Validate user login"""
        password_hash = self.generate_password_hash(login_data.password)
        user = await self.user_manager.get_user(login_data.email, password_hash, True)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )
        authorised_device = await self.device_manager.register_device_if_not_found(
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

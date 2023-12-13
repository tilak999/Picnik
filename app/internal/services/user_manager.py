import uuid

from pydantic import EmailStr

from app.internal.helper.base_service import BaseServiceClass
from prisma import Prisma


class UserManager(BaseServiceClass):
    """User management service"""

    def __init__(self, prisma: Prisma) -> None:
        super().__init__(prisma)

    async def create_new_user(
        self, email: EmailStr, password_hash: str, is_admin: bool
    ):
        db = await self.db()
        user = await db.user.create(
            data={
                "email": email,
                "password": password_hash,
                "name": email.split("@")[0],
                "isSystemAdmin": is_admin,
                "id": str(uuid.uuid4()),
            }
        )
        del user.password
        return user

    async def is_first_user(self):
        db = await self.db()
        count = await db.user.count()
        return count == 0

    async def get_user(self, email: str, password_hash: str, include_devices=False):
        db = await self.db()
        return await db.user.find_first(
            where={"email": email, "password": password_hash},
            include={"AuthorisedDevice": include_devices},
        )

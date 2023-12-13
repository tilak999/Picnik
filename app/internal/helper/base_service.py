import logging
from typing import Any, Optional
from pydantic import BaseModel
from prisma import Prisma


class AuditData(BaseModel):
    user_id: str
    subject: str
    message: str
    payload: Optional[Any]
    device_id: Optional[str]


class BaseServiceClass:
    def __init__(self, prisma: Optional[Prisma] = None, name=__name__) -> None:
        self.__prisma = prisma
        self.__name = name
        self.__init_logging()

    def get_name(self):
        return self.__name

    def __init_logging(self):
        log_format = "%(asctime)s - %(levelname)s: %(message)s"
        logging.basicConfig(format=log_format)
        self.logger = logging.getLogger(self.__name)

    async def get_config(self, key: str):
        db = await self.db()
        return await db.config.find_first(where={"key": key})

    async def db(self):
        if self.__prisma is None:
            raise ValueError("Prisma object is not provided to base class")
        if not self.__prisma.is_connected():
            await self.__prisma.connect()
        return self.__prisma

    async def audit_log(self, data: AuditData):
        db = await self.db()
        return await db.audit.create(
            data={
                "device_id": data.device_id or "",
                "message": data.message,
                "subject": data.subject,
                "user_id": data.user_id,
                "payload": data.payload,
            }
        )

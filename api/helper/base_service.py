import logging
import uuid
from prisma import Prisma


class BaseServiceClass:
    def __init__(self, prisma: Prisma) -> None:
        self.prisma = prisma

    def init_logging(self):
        FORMAT = "%(asctime)s - %(levelname)s: %(message)s"
        logging.basicConfig(format=FORMAT)
        self.logger = logging.getLogger(__name__)

    async def db(self):
        if not self.prisma.is_connected():
            await self.prisma.connect()
        return self.prisma

    async def audit_log(
        self, user_id: str, subject: str, message: str, payload: object, device_id: str
    ):
        return await self.prisma.audit.create(
            data={
                "id": str(uuid.uuid4()),
                "device_id": device_id,
                "message": message,
                "subject": subject,
                "user_id": user_id,
                "payload": payload,
            }
        )

from prisma import Prisma
from api.dto.devices import Device
from api.helper.base_service import BaseServiceClass


class DeviceManager(BaseServiceClass):
    def __init__(self, prisma: Prisma) -> None:
        super().__init__(prisma)

    async def checkIfDeviceExist(self, device: Device):
        db = await super().db()
        device = await db.authoriseddevice.find_first(
            where={"id": device.id, "user_id": device.user_id}
        )
        return device

    async def register(self, device: Device):
        db = await super().db()
        return await db.authoriseddevice.create(
            {"id": device.id, "name": device.name, "user_id": device.user_id}
        )

    async def register_device_if_not_found(self, user_id: str, device: Device):
        # check if device is in the list of authorised devices
        # or else create a new device entry and generate audit log
        device.user_id = user_id
        authorised_device = await self.checkIfDeviceExist(device)
        if authorised_device is None:
            authorised_device = await self.register(device)
        return authorised_device

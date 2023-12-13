from app.internal.helper.base_service import BaseServiceClass
from app.internal.schema.devices import Device


class DeviceManager(BaseServiceClass):
    async def check_device_exist(self, device: Device):
        if device.user_id is None:
            raise ValueError("User id is required")
        db = await self.db()
        return await db.authoriseddevice.find_first(
            where={"id": device.id, "user_id": device.user_id}
        )

    async def register(self, device: Device):
        if device.user_id is None:
            raise ValueError("User id is required")
        db = await self.db()
        return await db.authoriseddevice.create(
            {"id": device.id, "name": device.name, "user_id": device.user_id}
        )

    async def register_device_if_not_found(self, user_id: str, device: Device):
        # check if device is in the list of authorised devices
        # or else create a new device entry and generate audit log
        device.user_id = user_id
        authorised_device = await self.check_device_exist(device)
        if authorised_device is None:
            authorised_device = await self.register(device)
        return authorised_device

from app.internal.schema.devices import Device
from app.internal.schema.user import User


class LoginPayload(User):
    device: Device

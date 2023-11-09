from api.dto.devices import Device
from api.dto.user import User


class LoginPayload(User):
    device: Device

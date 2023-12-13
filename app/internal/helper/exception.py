class ServiceException(Exception):
    def __str__(self) -> str:
        return self.name + " -- " + self.message

    def __init__(self, name: str, message: str):
        self.name = name
        self.message = message

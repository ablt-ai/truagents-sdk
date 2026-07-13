from enum import Enum


class PhoneSourceEnum(str, Enum):
    ADMIN = "admin"
    EXTERNAL_API = "external_api"
    IMPORT = "import"
    TWILIO = "twilio"

    def __str__(self) -> str:
        return str(self.value)

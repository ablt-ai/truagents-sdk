from enum import Enum


class EmailSourceEnum(str, Enum):
    ADMIN = "admin"
    EXTERNAL_API = "external_api"
    IMPORT = "import"
    SENDGRID = "sendgrid"

    def __str__(self) -> str:
        return str(self.value)

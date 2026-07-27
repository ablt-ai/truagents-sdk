from enum import Enum


class UnsubscribeGroupKind(str, Enum):
    EMAIL = "email"
    PHONE_NUMBER = "phone_number"

    def __str__(self) -> str:
        return str(self.value)

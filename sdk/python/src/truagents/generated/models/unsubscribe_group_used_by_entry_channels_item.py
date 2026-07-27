from enum import Enum


class UnsubscribeGroupUsedByEntryChannelsItem(str, Enum):
    EMAIL = "email"
    PHONE = "phone"
    SMS = "sms"

    def __str__(self) -> str:
        return str(self.value)

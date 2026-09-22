from enum import StrEnum


class UnsubscribeGroupUsedByEntryChannelsItem(StrEnum):
    EMAIL = "email"
    PHONE = "phone"
    SMS = "sms"

    def __str__(self) -> str:
        return str(self.value)

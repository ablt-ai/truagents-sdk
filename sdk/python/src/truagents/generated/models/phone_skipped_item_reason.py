from enum import Enum


class PhoneSkippedItemReason(str, Enum):
    DUPLICATE_IDENTIFIER = "duplicate identifier"
    INVALID_PHONE_FORMAT = "invalid phone format"
    MISSING_IDENTIFIER = "missing identifier"
    MISSING_UNSUBSCRIBED = "missing unsubscribed"

    def __str__(self) -> str:
        return str(self.value)

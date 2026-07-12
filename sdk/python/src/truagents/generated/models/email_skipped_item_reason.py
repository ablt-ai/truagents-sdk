from enum import Enum


class EmailSkippedItemReason(str, Enum):
    DUPLICATE_IDENTIFIER = "duplicate identifier"
    INVALID_EMAIL_FORMAT = "invalid email format"
    MISSING_IDENTIFIER = "missing identifier"
    MISSING_UNSUBSCRIBED = "missing unsubscribed"

    def __str__(self) -> str:
        return str(self.value)

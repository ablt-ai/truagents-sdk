from enum import Enum


class InvalidItemErrorItemError(str, Enum):
    DUPLICATE_IDENTIFIER = "duplicate identifier"
    INVALID_EMAIL_FORMAT = "invalid email format"
    INVALID_PHONE_FORMAT = "invalid phone format"
    MISSING_IDENTIFIER = "missing identifier"

    def __str__(self) -> str:
        return str(self.value)

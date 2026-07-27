from enum import Enum


class InvalidItemErrorError(str, Enum):
    INVALID_ITEM = "invalid_item"

    def __str__(self) -> str:
        return str(self.value)

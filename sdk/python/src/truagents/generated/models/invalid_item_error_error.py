from enum import StrEnum


class InvalidItemErrorError(StrEnum):
    INVALID_ITEM = "invalid_item"

    def __str__(self) -> str:
        return str(self.value)

from enum import StrEnum


class SourceEnum(StrEnum):
    ADMIN = "admin"
    API = "api"
    IMPORT = "import"
    USER_ACTION = "user_action"
    USER_INTENT = "user_intent"

    def __str__(self) -> str:
        return str(self.value)

from enum import Enum


class SourceEnum(str, Enum):
    ADMIN = "admin"
    API = "api"
    IMPORT = "import"
    USER_ACTION = "user_action"
    USER_INTENT = "user_intent"

    def __str__(self) -> str:
        return str(self.value)

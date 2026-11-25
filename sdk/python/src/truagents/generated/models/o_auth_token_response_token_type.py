from enum import StrEnum


class OAuthTokenResponseTokenType(StrEnum):
    BEARER = "Bearer"

    def __str__(self) -> str:
        return str(self.value)

from enum import StrEnum


class OAuthRefreshTokenRequestGrantType(StrEnum):
    REFRESH_TOKEN = "refresh_token"

    def __str__(self) -> str:
        return str(self.value)

from enum import StrEnum


class OAuthErrorResponseError(StrEnum):
    INVALID_CLIENT = "invalid_client"
    INVALID_GRANT = "invalid_grant"
    INVALID_REQUEST = "invalid_request"
    UNSUPPORTED_GRANT_TYPE = "unsupported_grant_type"

    def __str__(self) -> str:
        return str(self.value)

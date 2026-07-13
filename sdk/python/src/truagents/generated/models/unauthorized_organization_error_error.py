from enum import Enum


class UnauthorizedOrganizationErrorError(str, Enum):
    UNAUTHORIZED_ORGANIZATION = "unauthorized_organization"

    def __str__(self) -> str:
        return str(self.value)

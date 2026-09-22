from enum import StrEnum


class UnauthorizedOrganizationErrorError(StrEnum):
    UNAUTHORIZED_ORGANIZATION = "unauthorized_organization"

    def __str__(self) -> str:
        return str(self.value)

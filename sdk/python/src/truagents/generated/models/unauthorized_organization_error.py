from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.unauthorized_organization_error_error import (
    UnauthorizedOrganizationErrorError,
)

T = TypeVar("T", bound="UnauthorizedOrganizationError")


@_attrs_define
class UnauthorizedOrganizationError:
    """Error body returned on `403 unauthorized_organization`. See the `UnauthorizedOrganization` response component for
    the HTTP semantics and the design rationale.

        Example:
            {'error': 'unauthorized_organization', 'error_description': 'The provided org_slug is not authorized for this
                API key.', 'org_slug': 'acme-cop'}

        Attributes:
            error (UnauthorizedOrganizationErrorError):
            error_description (str): Human-readable description suitable for logging.
            org_slug (str): The `org_slug` that was targeted — usually the value the caller supplied, echoed back so a typo
                is visible in the caller's own logs without the server confirming whether the slug exists. In the defensive
                N1-fallback path (the key's own default organization is somehow not in its authorized set), the server-resolved
                default slug appears here instead.
    """

    error: UnauthorizedOrganizationErrorError
    error_description: str
    org_slug: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        error = self.error.value

        error_description = self.error_description

        org_slug = self.org_slug

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "error": error,
                "error_description": error_description,
                "org_slug": org_slug,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        error = UnauthorizedOrganizationErrorError(d.pop("error"))

        error_description = d.pop("error_description")

        org_slug = d.pop("org_slug")

        unauthorized_organization_error = cls(
            error=error,
            error_description=error_description,
            org_slug=org_slug,
        )

        unauthorized_organization_error.additional_properties = d
        return unauthorized_organization_error

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties

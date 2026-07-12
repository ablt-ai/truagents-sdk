from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.o_auth_error_response_error import OAuthErrorResponseError
from ..types import UNSET, Unset

T = TypeVar("T", bound="OAuthErrorResponse")


@_attrs_define
class OAuthErrorResponse:
    """RFC 6749 §5.2 error envelope.

    Attributes:
        error (OAuthErrorResponseError): Machine-readable error code.
        error_description (str | Unset): Human-readable description suitable for logging.
        error_uri (str | Unset): Optional URI to a page describing the error.
    """

    error: OAuthErrorResponseError
    error_description: str | Unset = UNSET
    error_uri: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        error = self.error.value

        error_description = self.error_description

        error_uri = self.error_uri

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "error": error,
            }
        )
        if error_description is not UNSET:
            field_dict["error_description"] = error_description
        if error_uri is not UNSET:
            field_dict["error_uri"] = error_uri

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        error = OAuthErrorResponseError(d.pop("error"))

        error_description = d.pop("error_description", UNSET)

        error_uri = d.pop("error_uri", UNSET)

        o_auth_error_response = cls(
            error=error,
            error_description=error_description,
            error_uri=error_uri,
        )

        o_auth_error_response.additional_properties = d
        return o_auth_error_response

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

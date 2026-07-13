from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.o_auth_refresh_token_request_grant_type import (
    OAuthRefreshTokenRequestGrantType,
)

T = TypeVar("T", bound="OAuthRefreshTokenRequest")


@_attrs_define
class OAuthRefreshTokenRequest:
    """Refresh grant. The supplied `refresh_token` is invalidated on success; the response contains a fresh refresh token
    that must be stored atomically.

        Attributes:
            grant_type (OAuthRefreshTokenRequestGrantType):
            refresh_token (str): The most recent refresh token issued for this `client_id`.
    """

    grant_type: OAuthRefreshTokenRequestGrantType
    refresh_token: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        grant_type = self.grant_type.value

        refresh_token = self.refresh_token

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "grant_type": grant_type,
                "refresh_token": refresh_token,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        grant_type = OAuthRefreshTokenRequestGrantType(d.pop("grant_type"))

        refresh_token = d.pop("refresh_token")

        o_auth_refresh_token_request = cls(
            grant_type=grant_type,
            refresh_token=refresh_token,
        )

        o_auth_refresh_token_request.additional_properties = d
        return o_auth_refresh_token_request

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

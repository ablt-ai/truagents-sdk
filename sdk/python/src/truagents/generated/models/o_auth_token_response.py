from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.o_auth_token_response_token_type import OAuthTokenResponseTokenType

T = TypeVar("T", bound="OAuthTokenResponse")


@_attrs_define
class OAuthTokenResponse:
    """
    Attributes:
        access_token (str): Opaque bearer token (prefix `tru_at_`). Send on every API request as `Authorization: Bearer
            <access_token>`. Example: tru_at_<access_token>.
        token_type (OAuthTokenResponseTokenType):
        expires_in (int): Seconds until the access token expires. Example: 900.
        refresh_token (str): Opaque refresh token (prefix `tru_rt_`). Single-use; store atomically. Example:
            tru_rt_<refresh_token>.
        refresh_expires_in (int): Seconds until the refresh token expires. Example: 2592000.
    """

    access_token: str
    token_type: OAuthTokenResponseTokenType
    expires_in: int
    refresh_token: str
    refresh_expires_in: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        access_token = self.access_token

        token_type = self.token_type.value

        expires_in = self.expires_in

        refresh_token = self.refresh_token

        refresh_expires_in = self.refresh_expires_in

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "access_token": access_token,
                "token_type": token_type,
                "expires_in": expires_in,
                "refresh_token": refresh_token,
                "refresh_expires_in": refresh_expires_in,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        access_token = d.pop("access_token")

        token_type = OAuthTokenResponseTokenType(d.pop("token_type"))

        expires_in = d.pop("expires_in")

        refresh_token = d.pop("refresh_token")

        refresh_expires_in = d.pop("refresh_expires_in")

        o_auth_token_response = cls(
            access_token=access_token,
            token_type=token_type,
            expires_in=expires_in,
            refresh_token=refresh_token,
            refresh_expires_in=refresh_expires_in,
        )

        o_auth_token_response.additional_properties = d
        return o_auth_token_response

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

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.o_auth_client_credentials_request_grant_type import (
    OAuthClientCredentialsRequestGrantType,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="OAuthClientCredentialsRequest")


@_attrs_define
class OAuthClientCredentialsRequest:
    """Initial-authentication grant. Credentials may be sent via HTTP Basic (preferred) or as body fields. Per RFC 6749
    §2.3.1, both `client_id` and `client_secret` must be provided together when not using HTTP Basic.

        Attributes:
            grant_type (OAuthClientCredentialsRequestGrantType):
            client_id (str | Unset): Opaque client identifier. Required when credentials are not sent via HTTP Basic.
            client_secret (str | Unset): Plaintext client secret (prefixed `tru_cs_`). Required when credentials are not
                sent via HTTP Basic.
    """

    grant_type: OAuthClientCredentialsRequestGrantType
    client_id: str | Unset = UNSET
    client_secret: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        grant_type = self.grant_type.value

        client_id = self.client_id

        client_secret = self.client_secret

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "grant_type": grant_type,
            }
        )
        if client_id is not UNSET:
            field_dict["client_id"] = client_id
        if client_secret is not UNSET:
            field_dict["client_secret"] = client_secret

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        grant_type = OAuthClientCredentialsRequestGrantType(d.pop("grant_type"))

        client_id = d.pop("client_id", UNSET)

        client_secret = d.pop("client_secret", UNSET)

        o_auth_client_credentials_request = cls(
            grant_type=grant_type,
            client_id=client_id,
            client_secret=client_secret,
        )

        o_auth_client_credentials_request.additional_properties = d
        return o_auth_client_credentials_request

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

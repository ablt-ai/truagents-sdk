from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="EmailUnsubscribeItem")


@_attrs_define
class EmailUnsubscribeItem:
    """
    Attributes:
        email (str):
        unsubscribed (bool): `true` to opt-out, `false` to opt-in.
    """

    email: str
    unsubscribed: bool

    def to_dict(self) -> dict[str, Any]:
        email = self.email

        unsubscribed = self.unsubscribed

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "email": email,
                "unsubscribed": unsubscribed,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        email = d.pop("email")

        unsubscribed = d.pop("unsubscribed")

        email_unsubscribe_item = cls(
            email=email,
            unsubscribed=unsubscribed,
        )

        return email_unsubscribe_item

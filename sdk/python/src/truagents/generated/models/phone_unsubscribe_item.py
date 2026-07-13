from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="PhoneUnsubscribeItem")


@_attrs_define
class PhoneUnsubscribeItem:
    """
    Attributes:
        phone (str): Phone number in E.164 format. Non-E.164 input is rejected per-item with `reason: "invalid phone
            format"`. Example: +15551234567.
        unsubscribed (bool):
    """

    phone: str
    unsubscribed: bool

    def to_dict(self) -> dict[str, Any]:
        phone = self.phone

        unsubscribed = self.unsubscribed

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "phone": phone,
                "unsubscribed": unsubscribed,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        phone = d.pop("phone")

        unsubscribed = d.pop("unsubscribed")

        phone_unsubscribe_item = cls(
            phone=phone,
            unsubscribed=unsubscribed,
        )

        return phone_unsubscribe_item

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="PhoneUnsubscribeItem")


@_attrs_define
class PhoneUnsubscribeItem:
    """
    Attributes:
        phone (str): Phone number in E.164 format. A non-E.164 value aborts the entire batch with `400 invalid_item`
            (`item_error: "invalid phone format"`) and zero rows persisted. Example: +15551234567.
    """

    phone: str

    def to_dict(self) -> dict[str, Any]:
        phone = self.phone

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "phone": phone,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        phone = d.pop("phone")

        phone_unsubscribe_item = cls(
            phone=phone,
        )

        return phone_unsubscribe_item

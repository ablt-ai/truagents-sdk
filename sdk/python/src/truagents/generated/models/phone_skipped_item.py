from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.phone_skipped_item_reason import PhoneSkippedItemReason
from ..types import UNSET, Unset

T = TypeVar("T", bound="PhoneSkippedItem")


@_attrs_define
class PhoneSkippedItem:
    """An input item rejected by per-item validation. Echoes the original item fields plus a `reason`.

    Attributes:
        reason (PhoneSkippedItemReason):
        phone (str | Unset): Echoed from input when present.
        unsubscribed (bool | Unset): Echoed from input when present.
    """

    reason: PhoneSkippedItemReason
    phone: str | Unset = UNSET
    unsubscribed: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        reason = self.reason.value

        phone = self.phone

        unsubscribed = self.unsubscribed

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "reason": reason,
            }
        )
        if phone is not UNSET:
            field_dict["phone"] = phone
        if unsubscribed is not UNSET:
            field_dict["unsubscribed"] = unsubscribed

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        reason = PhoneSkippedItemReason(d.pop("reason"))

        phone = d.pop("phone", UNSET)

        unsubscribed = d.pop("unsubscribed", UNSET)

        phone_skipped_item = cls(
            reason=reason,
            phone=phone,
            unsubscribed=unsubscribed,
        )

        phone_skipped_item.additional_properties = d
        return phone_skipped_item

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

from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="EmailUnsubscribeUpdatedEntry")


@_attrs_define
class EmailUnsubscribeUpdatedEntry:
    """
    Attributes:
        email (str): Echoed from the input item.
        unsubscribed (bool): Echoed from the input item.
        updated_at (datetime.datetime): Row's current state-change timestamp. Compare against a previously-observed
            value for the same identifier to distinguish a real state change from an idempotent no-op.
    """

    email: str
    unsubscribed: bool
    updated_at: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        email = self.email

        unsubscribed = self.unsubscribed

        updated_at = self.updated_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "email": email,
                "unsubscribed": unsubscribed,
                "updated_at": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        email = d.pop("email")

        unsubscribed = d.pop("unsubscribed")

        updated_at = datetime.datetime.fromisoformat(d.pop("updated_at"))

        email_unsubscribe_updated_entry = cls(
            email=email,
            unsubscribed=unsubscribed,
            updated_at=updated_at,
        )

        email_unsubscribe_updated_entry.additional_properties = d
        return email_unsubscribe_updated_entry

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

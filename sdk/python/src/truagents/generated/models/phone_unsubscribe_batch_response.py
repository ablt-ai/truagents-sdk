from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.phone_unsubscribe_updated_entry import PhoneUnsubscribeUpdatedEntry


T = TypeVar("T", bound="PhoneUnsubscribeBatchResponse")


@_attrs_define
class PhoneUnsubscribeBatchResponse:
    """
    Example:
        {'group_id': 'ug_ckxyz123', 'processed': 1, 'updated': [{'phone': '+15551234567', 'unsubscribed': True,
            'updated_at': '2026-04-15T10:30:00Z'}]}

    Attributes:
        group_id (str): Group the batch was applied to — the one you targeted, or the one your `org_slug` / default
            organization resolved to. Example: ug_ckxyz123.
        processed (int): Count of items written — always `items.length` on a 200 (the batch is all-or-nothing).
            Idempotent writes (item already at requested state) are counted.
        updated (list[PhoneUnsubscribeUpdatedEntry]): One entry per input item, in input order.
    """

    group_id: str
    processed: int
    updated: list[PhoneUnsubscribeUpdatedEntry]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        group_id = self.group_id

        processed = self.processed

        updated = []
        for updated_item_data in self.updated:
            updated_item = updated_item_data.to_dict()
            updated.append(updated_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "group_id": group_id,
                "processed": processed,
                "updated": updated,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.phone_unsubscribe_updated_entry import (
            PhoneUnsubscribeUpdatedEntry,
        )

        d = dict(src_dict)
        group_id = d.pop("group_id")

        processed = d.pop("processed")

        updated = []
        _updated = d.pop("updated")
        for updated_item_data in _updated:
            updated_item = PhoneUnsubscribeUpdatedEntry.from_dict(updated_item_data)

            updated.append(updated_item)

        phone_unsubscribe_batch_response = cls(
            group_id=group_id,
            processed=processed,
            updated=updated,
        )

        phone_unsubscribe_batch_response.additional_properties = d
        return phone_unsubscribe_batch_response

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

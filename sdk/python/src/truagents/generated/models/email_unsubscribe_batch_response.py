from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.email_skipped_item import EmailSkippedItem
    from ..models.email_unsubscribe_updated_entry import EmailUnsubscribeUpdatedEntry


T = TypeVar("T", bound="EmailUnsubscribeBatchResponse")


@_attrs_define
class EmailUnsubscribeBatchResponse:
    """
    Example:
        {'org_slug': 'acme-corp', 'processed': 2, 'updated': [{'email': 'john@example.com', 'unsubscribed': True,
            'updated_at': '2026-04-15T10:30:00Z'}, {'email': 'alice@example.com', 'unsubscribed': False, 'updated_at':
            '2026-03-02T14:11:42Z'}], 'skipped_items': []}

    Attributes:
        org_slug (str): Organization the batch was applied to — the value you supplied, or your key's default
            organization when you omitted it. Example: acme-corp.
        processed (int): Count of items accepted into `updated` — equal to `items.length − skipped_items.length`.
            Idempotent writes (item already at requested state) are counted.
        updated (list[EmailUnsubscribeUpdatedEntry]): One entry per accepted input item, in input order.
        skipped_items (list[EmailSkippedItem]): Items rejected by per-item validation; each carries the original field
            echoes plus a `reason`.
    """

    org_slug: str
    processed: int
    updated: list[EmailUnsubscribeUpdatedEntry]
    skipped_items: list[EmailSkippedItem]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        org_slug = self.org_slug

        processed = self.processed

        updated = []
        for updated_item_data in self.updated:
            updated_item = updated_item_data.to_dict()
            updated.append(updated_item)

        skipped_items = []
        for skipped_items_item_data in self.skipped_items:
            skipped_items_item = skipped_items_item_data.to_dict()
            skipped_items.append(skipped_items_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "org_slug": org_slug,
                "processed": processed,
                "updated": updated,
                "skipped_items": skipped_items,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.email_skipped_item import EmailSkippedItem
        from ..models.email_unsubscribe_updated_entry import EmailUnsubscribeUpdatedEntry

        d = dict(src_dict)
        org_slug = d.pop("org_slug")

        processed = d.pop("processed")

        updated = []
        _updated = d.pop("updated")
        for updated_item_data in _updated:
            updated_item = EmailUnsubscribeUpdatedEntry.from_dict(updated_item_data)

            updated.append(updated_item)

        skipped_items = []
        _skipped_items = d.pop("skipped_items")
        for skipped_items_item_data in _skipped_items:
            skipped_items_item = EmailSkippedItem.from_dict(skipped_items_item_data)

            skipped_items.append(skipped_items_item)

        email_unsubscribe_batch_response = cls(
            org_slug=org_slug,
            processed=processed,
            updated=updated,
            skipped_items=skipped_items,
        )

        email_unsubscribe_batch_response.additional_properties = d
        return email_unsubscribe_batch_response

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

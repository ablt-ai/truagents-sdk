from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.email_unsubscribe_item import EmailUnsubscribeItem


T = TypeVar("T", bound="EmailUnsubscribeBatchRequest")


@_attrs_define
class EmailUnsubscribeBatchRequest:
    """
    Example:
        {'org_slug': 'acme-corp', 'items': [{'email': 'john@example.com', 'unsubscribed': True}, {'email':
            'alice@example.com', 'unsubscribed': False}]}

    Attributes:
        items (list[EmailUnsubscribeItem]): Up to 10,000 items per request. Items are processed in array order; partial
            failures do not roll back accepted items.
        org_slug (str | Unset): Organization to write to. Must be in your `client_id`'s authorized set. Omit to use the
            key's default organization. One batch targets exactly one organization — to write to several organizations, send
            one request per organization. Example: acme-corp.
    """

    items: list[EmailUnsubscribeItem]
    org_slug: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        items = []
        for items_item_data in self.items:
            items_item = items_item_data.to_dict()
            items.append(items_item)

        org_slug = self.org_slug

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "items": items,
            }
        )
        if org_slug is not UNSET:
            field_dict["org_slug"] = org_slug

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.email_unsubscribe_item import EmailUnsubscribeItem

        d = dict(src_dict)
        items = []
        _items = d.pop("items")
        for items_item_data in _items:
            items_item = EmailUnsubscribeItem.from_dict(items_item_data)

            items.append(items_item)

        org_slug = d.pop("org_slug", UNSET)

        email_unsubscribe_batch_request = cls(
            items=items,
            org_slug=org_slug,
        )

        email_unsubscribe_batch_request.additional_properties = d
        return email_unsubscribe_batch_request

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

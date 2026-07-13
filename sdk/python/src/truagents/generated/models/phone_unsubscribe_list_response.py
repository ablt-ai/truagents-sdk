from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.phone_unsubscribe_record import PhoneUnsubscribeRecord


T = TypeVar("T", bound="PhoneUnsubscribeListResponse")


@_attrs_define
class PhoneUnsubscribeListResponse:
    """
    Example:
        {'org_slug': 'acme-corp', 'data': [{'phone': '+15551234567', 'unsubscribed': True, 'source': 'twilio',
            'updated_at': '2026-04-12T16:22:01Z'}], 'next_cursor': None, 'has_more': False}

    Attributes:
        org_slug (str): Organization this page belongs to — the value you supplied, the one carried by `cursor`, or your
            key's default organization when neither was provided. Example: acme-corp.
        data (list[PhoneUnsubscribeRecord]):
        next_cursor (None | str): Pass to the `cursor` query parameter to fetch the next page. `null` when no more
            results are available. See the `Cursor` parameter for the encoding contract.
        has_more (bool):
    """

    org_slug: str
    data: list[PhoneUnsubscribeRecord]
    next_cursor: None | str
    has_more: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        org_slug = self.org_slug

        data = []
        for data_item_data in self.data:
            data_item = data_item_data.to_dict()
            data.append(data_item)

        next_cursor: None | str
        next_cursor = self.next_cursor

        has_more = self.has_more

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "org_slug": org_slug,
                "data": data,
                "next_cursor": next_cursor,
                "has_more": has_more,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.phone_unsubscribe_record import PhoneUnsubscribeRecord

        d = dict(src_dict)
        org_slug = d.pop("org_slug")

        data = []
        _data = d.pop("data")
        for data_item_data in _data:
            data_item = PhoneUnsubscribeRecord.from_dict(data_item_data)

            data.append(data_item)

        def _parse_next_cursor(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        next_cursor = _parse_next_cursor(d.pop("next_cursor"))

        has_more = d.pop("has_more")

        phone_unsubscribe_list_response = cls(
            org_slug=org_slug,
            data=data,
            next_cursor=next_cursor,
            has_more=has_more,
        )

        phone_unsubscribe_list_response.additional_properties = d
        return phone_unsubscribe_list_response

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

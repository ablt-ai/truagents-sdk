from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.email_unsubscribe_record import EmailUnsubscribeRecord


T = TypeVar("T", bound="EmailUnsubscribeListResponse")


@_attrs_define
class EmailUnsubscribeListResponse:
    """
    Example:
        {'group_id': 'ug_ckxyz123', 'data': [{'email': 'john@example.com', 'unsubscribed': True, 'source': 'api',
            'updated_at': '2026-04-15T10:30:00Z'}, {'email': 'alice@example.com', 'unsubscribed': False, 'source': 'admin',
            'updated_at': '2026-04-13T09:00:00Z'}], 'next_cursor': 'eyJncm91cF9pZCI6InVnX2NreHl6MTIzIiwibGFzdF91cGRhdGVkX2F0
            IjoiMjAyNi0wNC0xM1QwOTowMDowMFoiLCJsYXN0X2lkIjoicmVjX2NrN2YyYTlkMSJ9', 'has_more': True}

    Attributes:
        group_id (str): Group this page belongs to — the one you targeted, or the one your `org_slug` / default
            organization resolved to. Example: ug_ckxyz123.
        data (list[EmailUnsubscribeRecord]):
        next_cursor (None | str): Pass to the `cursor` query parameter to fetch the next page. `null` when no more
            results are available. See the `Cursor` parameter for the encoding contract.
        has_more (bool):
    """

    group_id: str
    data: list[EmailUnsubscribeRecord]
    next_cursor: None | str
    has_more: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        group_id = self.group_id

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
                "group_id": group_id,
                "data": data,
                "next_cursor": next_cursor,
                "has_more": has_more,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.email_unsubscribe_record import EmailUnsubscribeRecord

        d = dict(src_dict)
        group_id = d.pop("group_id")

        data = []
        _data = d.pop("data")
        for data_item_data in _data:
            data_item = EmailUnsubscribeRecord.from_dict(data_item_data)

            data.append(data_item)

        def _parse_next_cursor(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        next_cursor = _parse_next_cursor(d.pop("next_cursor"))

        has_more = d.pop("has_more")

        email_unsubscribe_list_response = cls(
            group_id=group_id,
            data=data,
            next_cursor=next_cursor,
            has_more=has_more,
        )

        email_unsubscribe_list_response.additional_properties = d
        return email_unsubscribe_list_response

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

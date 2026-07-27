from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.unsubscribe_group import UnsubscribeGroup


T = TypeVar("T", bound="UnsubscribeGroupsResponse")


@_attrs_define
class UnsubscribeGroupsResponse:
    """
    Example:
        {'data': [{'id': 'ug_ckxyz123', 'name': 'Default email unsubscribes', 'description': None, 'kind': 'email',
            'unsubscribes': 1204, 'owner': 'acme-corp', 'used_by': [{'org': 'acme-corp', 'channels': ['email']}]}, {'id':
            'ug_ckshared9', 'name': 'Group-wide SMS + voice suppression', 'description': 'Shared across the ACME family',
            'kind': 'phone_number', 'unsubscribes': 87, 'owner': None, 'used_by': [{'org': 'acme-corp', 'channels': ['sms',
            'phone']}]}]}

    Attributes:
        data (list[UnsubscribeGroup]):
    """

    data: list[UnsubscribeGroup]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = []
        for data_item_data in self.data:
            data_item = data_item_data.to_dict()
            data.append(data_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data": data,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.unsubscribe_group import UnsubscribeGroup

        d = dict(src_dict)
        data = []
        _data = d.pop("data")
        for data_item_data in _data:
            data_item = UnsubscribeGroup.from_dict(data_item_data)

            data.append(data_item)

        unsubscribe_groups_response = cls(
            data=data,
        )

        unsubscribe_groups_response.additional_properties = d
        return unsubscribe_groups_response

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

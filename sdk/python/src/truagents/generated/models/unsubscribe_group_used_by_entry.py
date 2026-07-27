from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.unsubscribe_group_used_by_entry_channels_item import (
    UnsubscribeGroupUsedByEntryChannelsItem,
)

T = TypeVar("T", bound="UnsubscribeGroupUsedByEntry")


@_attrs_define
class UnsubscribeGroupUsedByEntry:
    """
    Attributes:
        org (str): Slug of one of YOUR authorized organizations using this group. Example: acme-corp.
        channels (list[UnsubscribeGroupUsedByEntryChannelsItem]): URL channels that organization routes through this
            group.
    """

    org: str
    channels: list[UnsubscribeGroupUsedByEntryChannelsItem]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        org = self.org

        channels = []
        for channels_item_data in self.channels:
            channels_item = channels_item_data.value
            channels.append(channels_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "org": org,
                "channels": channels,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        org = d.pop("org")

        channels = []
        _channels = d.pop("channels")
        for channels_item_data in _channels:
            channels_item = UnsubscribeGroupUsedByEntryChannelsItem(channels_item_data)

            channels.append(channels_item)

        unsubscribe_group_used_by_entry = cls(
            org=org,
            channels=channels,
        )

        unsubscribe_group_used_by_entry.additional_properties = d
        return unsubscribe_group_used_by_entry

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

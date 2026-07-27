from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.unsubscribe_group_kind import UnsubscribeGroupKind

if TYPE_CHECKING:
    from ..models.unsubscribe_group_used_by_entry import UnsubscribeGroupUsedByEntry


T = TypeVar("T", bound="UnsubscribeGroup")


@_attrs_define
class UnsubscribeGroup:
    """
    Attributes:
        id (str): Client-visible group id — pass as `group_id` when targeting this group. Example: ug_ckxyz123.
        name (None | str): Admin-assigned label, or `null`.
        description (None | str): Admin-assigned description, or `null`.
        kind (UnsubscribeGroupKind): Which endpoints accept the group: `email` for `/email/*`; `phone_number` for
            `/sms/*` and `/phone/*`.
        unsubscribes (int): Count of identifiers currently opted out in the group. Opted-back-in records are excluded.
        owner (None | str): Owning organization's slug, or `null` when the owner is outside your authorized set (the
            group is reachable only because one of your organizations uses it).
        used_by (list[UnsubscribeGroupUsedByEntry]): Which of YOUR authorized organizations use the group, per channel.
            Organizations outside your authorized set never appear.
    """

    id: str
    name: None | str
    description: None | str
    kind: UnsubscribeGroupKind
    unsubscribes: int
    owner: None | str
    used_by: list[UnsubscribeGroupUsedByEntry]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name: None | str
        name = self.name

        description: None | str
        description = self.description

        kind = self.kind.value

        unsubscribes = self.unsubscribes

        owner: None | str
        owner = self.owner

        used_by = []
        for used_by_item_data in self.used_by:
            used_by_item = used_by_item_data.to_dict()
            used_by.append(used_by_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "description": description,
                "kind": kind,
                "unsubscribes": unsubscribes,
                "owner": owner,
                "used_by": used_by,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.unsubscribe_group_used_by_entry import UnsubscribeGroupUsedByEntry

        d = dict(src_dict)
        id = d.pop("id")

        def _parse_name(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        name = _parse_name(d.pop("name"))

        def _parse_description(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        description = _parse_description(d.pop("description"))

        kind = UnsubscribeGroupKind(d.pop("kind"))

        unsubscribes = d.pop("unsubscribes")

        def _parse_owner(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        owner = _parse_owner(d.pop("owner"))

        used_by = []
        _used_by = d.pop("used_by")
        for used_by_item_data in _used_by:
            used_by_item = UnsubscribeGroupUsedByEntry.from_dict(used_by_item_data)

            used_by.append(used_by_item)

        unsubscribe_group = cls(
            id=id,
            name=name,
            description=description,
            kind=kind,
            unsubscribes=unsubscribes,
            owner=owner,
            used_by=used_by,
        )

        unsubscribe_group.additional_properties = d
        return unsubscribe_group

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

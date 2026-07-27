from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.invalid_item_error_error import InvalidItemErrorError
from ..models.invalid_item_error_item_error import InvalidItemErrorItemError

T = TypeVar("T", bound="InvalidItemError")


@_attrs_define
class InvalidItemError:
    """Error body returned when any batch item fails validation. The batch is all-or-nothing: zero rows were persisted. Fix
    the item at `item_index` and resend the whole batch.

        Example:
            {'error': 'invalid_item', 'error_description': 'Batch rejected: item 2 is invalid; no rows were persisted.',
                'item_index': 2, 'item_error': 'invalid email format'}

        Attributes:
            error (InvalidItemErrorError):
            error_description (str):
            item_index (int): Zero-based index of the FIRST invalid item in the submitted array.
            item_error (InvalidItemErrorItemError): Stable reason string for the invalid item.
    """

    error: InvalidItemErrorError
    error_description: str
    item_index: int
    item_error: InvalidItemErrorItemError
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        error = self.error.value

        error_description = self.error_description

        item_index = self.item_index

        item_error = self.item_error.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "error": error,
                "error_description": error_description,
                "item_index": item_index,
                "item_error": item_error,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        error = InvalidItemErrorError(d.pop("error"))

        error_description = d.pop("error_description")

        item_index = d.pop("item_index")

        item_error = InvalidItemErrorItemError(d.pop("item_error"))

        invalid_item_error = cls(
            error=error,
            error_description=error_description,
            item_index=item_index,
            item_error=item_error,
        )

        invalid_item_error.additional_properties = d
        return invalid_item_error

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

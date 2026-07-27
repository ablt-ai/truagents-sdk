from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="EmailUnsubscribeItem")


@_attrs_define
class EmailUnsubscribeItem:
    """
    Attributes:
        email (str): A malformed email aborts the entire batch with `400 invalid_item` (`item_error: "invalid email
            format"`) and zero rows persisted.
    """

    email: str

    def to_dict(self) -> dict[str, Any]:
        email = self.email

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "email": email,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        email = d.pop("email")

        email_unsubscribe_item = cls(
            email=email,
        )

        return email_unsubscribe_item

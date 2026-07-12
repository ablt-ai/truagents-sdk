from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.email_source_enum import EmailSourceEnum

T = TypeVar("T", bound="EmailUnsubscribeRecord")


@_attrs_define
class EmailUnsubscribeRecord:
    """
    Example:
        {'email': 'john@example.com', 'unsubscribed': True, 'source': 'external_api', 'updated_at':
            '2026-04-15T10:30:00Z'}

    Attributes:
        email (str): Email address, normalized to lowercase canonical form.
        unsubscribed (bool): `true` = opted out (TruAgents will not send on this channel).
        source (EmailSourceEnum): The category of writer responsible for the row's most recent state change on the email
            channel.

            - `external_api` — pushed by the partner via this API.
            - `sendgrid` — derived from a SendGrid unsubscribe event.
            - `admin` — manually changed by a TruAgents administrator.
            - `import` — created during initial backfill from legacy per-contact flags.
        updated_at (datetime.datetime): ISO 8601 timestamp of the most recent state change.
    """

    email: str
    unsubscribed: bool
    source: EmailSourceEnum
    updated_at: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        email = self.email

        unsubscribed = self.unsubscribed

        source = self.source.value

        updated_at = self.updated_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "email": email,
                "unsubscribed": unsubscribed,
                "source": source,
                "updated_at": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        email = d.pop("email")

        unsubscribed = d.pop("unsubscribed")

        source = EmailSourceEnum(d.pop("source"))

        updated_at = datetime.datetime.fromisoformat(d.pop("updated_at"))

        email_unsubscribe_record = cls(
            email=email,
            unsubscribed=unsubscribed,
            source=source,
            updated_at=updated_at,
        )

        email_unsubscribe_record.additional_properties = d
        return email_unsubscribe_record

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

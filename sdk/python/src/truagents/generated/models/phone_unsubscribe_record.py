from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.source_enum import SourceEnum

T = TypeVar("T", bound="PhoneUnsubscribeRecord")


@_attrs_define
class PhoneUnsubscribeRecord:
    """Used by both `/api/v1/unsubscribe/sms` and `/api/v1/unsubscribe/phone` — the channel is implicit in the URL.

    Example:
        {'phone': '+15551234567', 'unsubscribed': True, 'source': 'user_action', 'updated_at': '2026-04-12T16:22:01Z'}

    Attributes:
        phone (str): Phone number in E.164 format. Example: +15551234567.
        unsubscribed (bool): `true` = opted out (TruAgents will not send on this channel).
        source (SourceEnum): The category of writer responsible for the row's most recent state change. The same five
            values apply to every channel (email, SMS, voice).

            - `api` — pushed by the partner via this API.
            - `admin` — manually changed by a TruAgents administrator.
            - `import` — bulk import: CSV upload, CRM sync (HubSpot / Salesforce / Mailchimp), or the one-time legacy
            backfill from pre-existing opt-out state.
            - `user_action` — recipient took a concrete provider-observed action: SendGrid unsubscribe link, SendGrid list-
            unsubscribe header, Twilio STOP / UNSUBSCRIBE keyword. Opt-ins via Twilio START / YES / UNSTOP emit the same
            source with `unsubscribed: false`.
            - `user_intent` — TruAgents inferred opt-out intent from an inbound message. The provider did not observe a
            subscription action; TruAgents inferred intent from the inbound message and acted on the recipient's behalf.
        updated_at (datetime.datetime): ISO 8601 timestamp of the most recent state change.
    """

    phone: str
    unsubscribed: bool
    source: SourceEnum
    updated_at: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        phone = self.phone

        unsubscribed = self.unsubscribed

        source = self.source.value

        updated_at = self.updated_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "phone": phone,
                "unsubscribed": unsubscribed,
                "source": source,
                "updated_at": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        phone = d.pop("phone")

        unsubscribed = d.pop("unsubscribed")

        source = SourceEnum(d.pop("source"))

        updated_at = datetime.datetime.fromisoformat(d.pop("updated_at"))

        phone_unsubscribe_record = cls(
            phone=phone,
            unsubscribed=unsubscribed,
            source=source,
            updated_at=updated_at,
        )

        phone_unsubscribe_record.additional_properties = d
        return phone_unsubscribe_record

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

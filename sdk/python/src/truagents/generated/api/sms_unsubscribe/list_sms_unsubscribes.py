import datetime
from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.phone_unsubscribe_list_response import PhoneUnsubscribeListResponse
from ...models.rest_error_response import RestErrorResponse
from ...models.unauthorized_organization_error import UnauthorizedOrganizationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    org_slug: str | Unset = UNSET,
    since: datetime.datetime | Unset = UNSET,
    until: datetime.datetime | Unset = UNSET,
    cursor: str | Unset = UNSET,
    limit: int | Unset = 100,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["org_slug"] = org_slug

    json_since: str | Unset = UNSET
    if not isinstance(since, Unset):
        json_since = since.isoformat()
    params["since"] = json_since

    json_until: str | Unset = UNSET
    if not isinstance(until, Unset):
        json_until = until.isoformat()
    params["until"] = json_until

    params["cursor"] = cursor

    params["limit"] = limit

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/unsubscribe/sms",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> (
    PhoneUnsubscribeListResponse
    | RestErrorResponse
    | UnauthorizedOrganizationError
    | None
):
    if response.status_code == 200:
        response_200 = PhoneUnsubscribeListResponse.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = RestErrorResponse.from_dict(response.json())

        return response_400

    if response.status_code == 401:
        response_401 = RestErrorResponse.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = UnauthorizedOrganizationError.from_dict(response.json())

        return response_403

    if response.status_code == 429:
        response_429 = RestErrorResponse.from_dict(response.json())

        return response_429

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[
    PhoneUnsubscribeListResponse | RestErrorResponse | UnauthorizedOrganizationError
]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    org_slug: str | Unset = UNSET,
    since: datetime.datetime | Unset = UNSET,
    until: datetime.datetime | Unset = UNSET,
    cursor: str | Unset = UNSET,
    limit: int | Unset = 100,
) -> Response[
    PhoneUnsubscribeListResponse | RestErrorResponse | UnauthorizedOrganizationError
]:
    """List SMS opt-out / opt-in records

     Returns the current state of SMS unsubscribe records for the organization addressed by `org_slug`
    (or the `client_id`'s default organization when omitted), ordered by `updated_at` descending. Treat
    the endpoint as a change stream: `since` / `until` bound the pagination window and `cursor` walks
    toward older records. Rate limited to 60 requests per minute per `client_id`.

    Args:
        org_slug (str | Unset):
        since (datetime.datetime | Unset):
        until (datetime.datetime | Unset):
        cursor (str | Unset):
        limit (int | Unset):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PhoneUnsubscribeListResponse | RestErrorResponse | UnauthorizedOrganizationError]
    """

    kwargs = _get_kwargs(
        org_slug=org_slug,
        since=since,
        until=until,
        cursor=cursor,
        limit=limit,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    org_slug: str | Unset = UNSET,
    since: datetime.datetime | Unset = UNSET,
    until: datetime.datetime | Unset = UNSET,
    cursor: str | Unset = UNSET,
    limit: int | Unset = 100,
) -> (
    PhoneUnsubscribeListResponse
    | RestErrorResponse
    | UnauthorizedOrganizationError
    | None
):
    """List SMS opt-out / opt-in records

     Returns the current state of SMS unsubscribe records for the organization addressed by `org_slug`
    (or the `client_id`'s default organization when omitted), ordered by `updated_at` descending. Treat
    the endpoint as a change stream: `since` / `until` bound the pagination window and `cursor` walks
    toward older records. Rate limited to 60 requests per minute per `client_id`.

    Args:
        org_slug (str | Unset):
        since (datetime.datetime | Unset):
        until (datetime.datetime | Unset):
        cursor (str | Unset):
        limit (int | Unset):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PhoneUnsubscribeListResponse | RestErrorResponse | UnauthorizedOrganizationError
    """

    return sync_detailed(
        client=client,
        org_slug=org_slug,
        since=since,
        until=until,
        cursor=cursor,
        limit=limit,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    org_slug: str | Unset = UNSET,
    since: datetime.datetime | Unset = UNSET,
    until: datetime.datetime | Unset = UNSET,
    cursor: str | Unset = UNSET,
    limit: int | Unset = 100,
) -> Response[
    PhoneUnsubscribeListResponse | RestErrorResponse | UnauthorizedOrganizationError
]:
    """List SMS opt-out / opt-in records

     Returns the current state of SMS unsubscribe records for the organization addressed by `org_slug`
    (or the `client_id`'s default organization when omitted), ordered by `updated_at` descending. Treat
    the endpoint as a change stream: `since` / `until` bound the pagination window and `cursor` walks
    toward older records. Rate limited to 60 requests per minute per `client_id`.

    Args:
        org_slug (str | Unset):
        since (datetime.datetime | Unset):
        until (datetime.datetime | Unset):
        cursor (str | Unset):
        limit (int | Unset):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PhoneUnsubscribeListResponse | RestErrorResponse | UnauthorizedOrganizationError]
    """

    kwargs = _get_kwargs(
        org_slug=org_slug,
        since=since,
        until=until,
        cursor=cursor,
        limit=limit,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    org_slug: str | Unset = UNSET,
    since: datetime.datetime | Unset = UNSET,
    until: datetime.datetime | Unset = UNSET,
    cursor: str | Unset = UNSET,
    limit: int | Unset = 100,
) -> (
    PhoneUnsubscribeListResponse
    | RestErrorResponse
    | UnauthorizedOrganizationError
    | None
):
    """List SMS opt-out / opt-in records

     Returns the current state of SMS unsubscribe records for the organization addressed by `org_slug`
    (or the `client_id`'s default organization when omitted), ordered by `updated_at` descending. Treat
    the endpoint as a change stream: `since` / `until` bound the pagination window and `cursor` walks
    toward older records. Rate limited to 60 requests per minute per `client_id`.

    Args:
        org_slug (str | Unset):
        since (datetime.datetime | Unset):
        until (datetime.datetime | Unset):
        cursor (str | Unset):
        limit (int | Unset):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PhoneUnsubscribeListResponse | RestErrorResponse | UnauthorizedOrganizationError
    """

    return (
        await asyncio_detailed(
            client=client,
            org_slug=org_slug,
            since=since,
            until=until,
            cursor=cursor,
            limit=limit,
        )
    ).parsed

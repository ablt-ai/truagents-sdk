from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.phone_unsubscribe_batch_request import PhoneUnsubscribeBatchRequest
from ...models.phone_unsubscribe_batch_response import PhoneUnsubscribeBatchResponse
from ...models.rest_error_response import RestErrorResponse
from ...models.unauthorized_organization_error import UnauthorizedOrganizationError
from ...types import Response


def _get_kwargs(
    *,
    body: PhoneUnsubscribeBatchRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/unsubscribe/sms",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> (
    PhoneUnsubscribeBatchResponse
    | RestErrorResponse
    | UnauthorizedOrganizationError
    | None
):
    if response.status_code == 200:
        response_200 = PhoneUnsubscribeBatchResponse.from_dict(response.json())

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

    if response.status_code == 422:
        response_422 = PhoneUnsubscribeBatchResponse.from_dict(response.json())

        return response_422

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
    PhoneUnsubscribeBatchResponse | RestErrorResponse | UnauthorizedOrganizationError
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
    body: PhoneUnsubscribeBatchRequest,
) -> Response[
    PhoneUnsubscribeBatchResponse | RestErrorResponse | UnauthorizedOrganizationError
]:
    """Push SMS opt-out / opt-in changes

     Apply a batch of `{ phone, unsubscribed }` state changes to one organization — the value supplied in
    `org_slug` (top-level body field) or the `client_id`'s default organization when omitted. Items are
    processed in array order; per-item failures do NOT roll back accepted items. Up to 10,000 items per
    request. Idempotent. Rate limited to 60 requests per minute per `client_id`.

    Args:
        body (PhoneUnsubscribeBatchRequest):  Example: {'org_slug': 'acme-corp', 'items':
            [{'phone': '+15551234567', 'unsubscribed': True}]}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PhoneUnsubscribeBatchResponse | RestErrorResponse | UnauthorizedOrganizationError]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    body: PhoneUnsubscribeBatchRequest,
) -> (
    PhoneUnsubscribeBatchResponse
    | RestErrorResponse
    | UnauthorizedOrganizationError
    | None
):
    """Push SMS opt-out / opt-in changes

     Apply a batch of `{ phone, unsubscribed }` state changes to one organization — the value supplied in
    `org_slug` (top-level body field) or the `client_id`'s default organization when omitted. Items are
    processed in array order; per-item failures do NOT roll back accepted items. Up to 10,000 items per
    request. Idempotent. Rate limited to 60 requests per minute per `client_id`.

    Args:
        body (PhoneUnsubscribeBatchRequest):  Example: {'org_slug': 'acme-corp', 'items':
            [{'phone': '+15551234567', 'unsubscribed': True}]}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PhoneUnsubscribeBatchResponse | RestErrorResponse | UnauthorizedOrganizationError
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: PhoneUnsubscribeBatchRequest,
) -> Response[
    PhoneUnsubscribeBatchResponse | RestErrorResponse | UnauthorizedOrganizationError
]:
    """Push SMS opt-out / opt-in changes

     Apply a batch of `{ phone, unsubscribed }` state changes to one organization — the value supplied in
    `org_slug` (top-level body field) or the `client_id`'s default organization when omitted. Items are
    processed in array order; per-item failures do NOT roll back accepted items. Up to 10,000 items per
    request. Idempotent. Rate limited to 60 requests per minute per `client_id`.

    Args:
        body (PhoneUnsubscribeBatchRequest):  Example: {'org_slug': 'acme-corp', 'items':
            [{'phone': '+15551234567', 'unsubscribed': True}]}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PhoneUnsubscribeBatchResponse | RestErrorResponse | UnauthorizedOrganizationError]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: PhoneUnsubscribeBatchRequest,
) -> (
    PhoneUnsubscribeBatchResponse
    | RestErrorResponse
    | UnauthorizedOrganizationError
    | None
):
    """Push SMS opt-out / opt-in changes

     Apply a batch of `{ phone, unsubscribed }` state changes to one organization — the value supplied in
    `org_slug` (top-level body field) or the `client_id`'s default organization when omitted. Items are
    processed in array order; per-item failures do NOT roll back accepted items. Up to 10,000 items per
    request. Idempotent. Rate limited to 60 requests per minute per `client_id`.

    Args:
        body (PhoneUnsubscribeBatchRequest):  Example: {'org_slug': 'acme-corp', 'items':
            [{'phone': '+15551234567', 'unsubscribed': True}]}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PhoneUnsubscribeBatchResponse | RestErrorResponse | UnauthorizedOrganizationError
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed

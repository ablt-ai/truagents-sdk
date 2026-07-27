from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.email_unsubscribe_batch_request import EmailUnsubscribeBatchRequest
from ...models.email_unsubscribe_batch_response import EmailUnsubscribeBatchResponse
from ...models.invalid_item_error import InvalidItemError
from ...models.rest_error_response import RestErrorResponse
from ...models.unauthorized_organization_error import UnauthorizedOrganizationError
from ...types import Response


def _get_kwargs(
    *,
    body: EmailUnsubscribeBatchRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/unsubscribe/email/remove",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> (
    EmailUnsubscribeBatchResponse
    | InvalidItemError
    | RestErrorResponse
    | RestErrorResponse
    | UnauthorizedOrganizationError
    | None
):
    if response.status_code == 200:
        response_200 = EmailUnsubscribeBatchResponse.from_dict(response.json())

        return response_200

    if response.status_code == 400:

        def _parse_response_400(data: object) -> InvalidItemError | RestErrorResponse:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                response_400_type_0 = InvalidItemError.from_dict(data)

                return response_400_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            response_400_type_1 = RestErrorResponse.from_dict(data)

            return response_400_type_1

        response_400 = _parse_response_400(response.json())

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
    EmailUnsubscribeBatchResponse
    | InvalidItemError
    | RestErrorResponse
    | RestErrorResponse
    | UnauthorizedOrganizationError
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
    body: EmailUnsubscribeBatchRequest,
) -> Response[
    EmailUnsubscribeBatchResponse
    | InvalidItemError
    | RestErrorResponse
    | RestErrorResponse
    | UnauthorizedOrganizationError
]:
    """Opt identifiers back in (email)

     Writes a batch of email opt-out / opt-in records, opting each identifier back in to the targeted
    group. The URL verb supplies the direction; request bodies carry no direction field. The batch is
    all-or-nothing: validated as a whole before anything is written; any invalid item returns `400
    invalid_item` with zero rows persisted. Target via `group_id` or `org_slug` (at most one), or omit
    both for the key's default organization. Rate limited to 60 requests per minute per `client_id`.

    Args:
        body (EmailUnsubscribeBatchRequest):  Example: {'org_slug': 'acme-corp', 'items':
            [{'email': 'john@example.com'}, {'email': 'alice@example.com'}]}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[EmailUnsubscribeBatchResponse | InvalidItemError | RestErrorResponse | RestErrorResponse | UnauthorizedOrganizationError]
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
    body: EmailUnsubscribeBatchRequest,
) -> (
    EmailUnsubscribeBatchResponse
    | InvalidItemError
    | RestErrorResponse
    | RestErrorResponse
    | UnauthorizedOrganizationError
    | None
):
    """Opt identifiers back in (email)

     Writes a batch of email opt-out / opt-in records, opting each identifier back in to the targeted
    group. The URL verb supplies the direction; request bodies carry no direction field. The batch is
    all-or-nothing: validated as a whole before anything is written; any invalid item returns `400
    invalid_item` with zero rows persisted. Target via `group_id` or `org_slug` (at most one), or omit
    both for the key's default organization. Rate limited to 60 requests per minute per `client_id`.

    Args:
        body (EmailUnsubscribeBatchRequest):  Example: {'org_slug': 'acme-corp', 'items':
            [{'email': 'john@example.com'}, {'email': 'alice@example.com'}]}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        EmailUnsubscribeBatchResponse | InvalidItemError | RestErrorResponse | RestErrorResponse | UnauthorizedOrganizationError
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: EmailUnsubscribeBatchRequest,
) -> Response[
    EmailUnsubscribeBatchResponse
    | InvalidItemError
    | RestErrorResponse
    | RestErrorResponse
    | UnauthorizedOrganizationError
]:
    """Opt identifiers back in (email)

     Writes a batch of email opt-out / opt-in records, opting each identifier back in to the targeted
    group. The URL verb supplies the direction; request bodies carry no direction field. The batch is
    all-or-nothing: validated as a whole before anything is written; any invalid item returns `400
    invalid_item` with zero rows persisted. Target via `group_id` or `org_slug` (at most one), or omit
    both for the key's default organization. Rate limited to 60 requests per minute per `client_id`.

    Args:
        body (EmailUnsubscribeBatchRequest):  Example: {'org_slug': 'acme-corp', 'items':
            [{'email': 'john@example.com'}, {'email': 'alice@example.com'}]}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[EmailUnsubscribeBatchResponse | InvalidItemError | RestErrorResponse | RestErrorResponse | UnauthorizedOrganizationError]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: EmailUnsubscribeBatchRequest,
) -> (
    EmailUnsubscribeBatchResponse
    | InvalidItemError
    | RestErrorResponse
    | RestErrorResponse
    | UnauthorizedOrganizationError
    | None
):
    """Opt identifiers back in (email)

     Writes a batch of email opt-out / opt-in records, opting each identifier back in to the targeted
    group. The URL verb supplies the direction; request bodies carry no direction field. The batch is
    all-or-nothing: validated as a whole before anything is written; any invalid item returns `400
    invalid_item` with zero rows persisted. Target via `group_id` or `org_slug` (at most one), or omit
    both for the key's default organization. Rate limited to 60 requests per minute per `client_id`.

    Args:
        body (EmailUnsubscribeBatchRequest):  Example: {'org_slug': 'acme-corp', 'items':
            [{'email': 'john@example.com'}, {'email': 'alice@example.com'}]}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        EmailUnsubscribeBatchResponse | InvalidItemError | RestErrorResponse | RestErrorResponse | UnauthorizedOrganizationError
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed

from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.rest_error_response import RestErrorResponse
from ...models.unsubscribe_groups_response import UnsubscribeGroupsResponse
from ...types import Response


def _get_kwargs() -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/unsubscribe-groups",
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> RestErrorResponse | UnsubscribeGroupsResponse | None:
    if response.status_code == 200:
        response_200 = UnsubscribeGroupsResponse.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = RestErrorResponse.from_dict(response.json())

        return response_401

    if response.status_code == 429:
        response_429 = RestErrorResponse.from_dict(response.json())

        return response_429

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[RestErrorResponse | UnsubscribeGroupsResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
) -> Response[RestErrorResponse | UnsubscribeGroupsResponse]:
    """Discover reachable unsubscribe groups

     Returns every unsubscribe group reachable with the credential — groups owned by an authorized
    organization plus groups any authorized organization uses on some channel. Cross-organization
    isolation applies: `owner` is `null` when the owning organization is outside the authorized set, and
    `used_by` lists only authorized organizations. Not paginated. Rate limited to 60 requests per minute
    per `client_id`.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[RestErrorResponse | UnsubscribeGroupsResponse]
    """

    kwargs = _get_kwargs()

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
) -> RestErrorResponse | UnsubscribeGroupsResponse | None:
    """Discover reachable unsubscribe groups

     Returns every unsubscribe group reachable with the credential — groups owned by an authorized
    organization plus groups any authorized organization uses on some channel. Cross-organization
    isolation applies: `owner` is `null` when the owning organization is outside the authorized set, and
    `used_by` lists only authorized organizations. Not paginated. Rate limited to 60 requests per minute
    per `client_id`.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        RestErrorResponse | UnsubscribeGroupsResponse
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
) -> Response[RestErrorResponse | UnsubscribeGroupsResponse]:
    """Discover reachable unsubscribe groups

     Returns every unsubscribe group reachable with the credential — groups owned by an authorized
    organization plus groups any authorized organization uses on some channel. Cross-organization
    isolation applies: `owner` is `null` when the owning organization is outside the authorized set, and
    `used_by` lists only authorized organizations. Not paginated. Rate limited to 60 requests per minute
    per `client_id`.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[RestErrorResponse | UnsubscribeGroupsResponse]
    """

    kwargs = _get_kwargs()

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
) -> RestErrorResponse | UnsubscribeGroupsResponse | None:
    """Discover reachable unsubscribe groups

     Returns every unsubscribe group reachable with the credential — groups owned by an authorized
    organization plus groups any authorized organization uses on some channel. Cross-organization
    isolation applies: `owner` is `null` when the owning organization is outside the authorized set, and
    `used_by` lists only authorized organizations. Not paginated. Rate limited to 60 requests per minute
    per `client_id`.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        RestErrorResponse | UnsubscribeGroupsResponse
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed

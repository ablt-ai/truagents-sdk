from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.o_auth_client_credentials_request import OAuthClientCredentialsRequest
from ...models.o_auth_error_response import OAuthErrorResponse
from ...models.o_auth_refresh_token_request import OAuthRefreshTokenRequest
from ...models.o_auth_token_response import OAuthTokenResponse
from ...models.rest_error_response import RestErrorResponse
from ...types import Response


def _get_kwargs(
    *,
    body: OAuthClientCredentialsRequest | OAuthRefreshTokenRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/oauth/token",
    }

    _kwargs["data"] = body.to_dict()
    headers["Content-Type"] = "application/x-www-form-urlencoded"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> OAuthErrorResponse | OAuthTokenResponse | RestErrorResponse | None:
    if response.status_code == 200:
        response_200 = OAuthTokenResponse.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = OAuthErrorResponse.from_dict(response.json())

        return response_400

    if response.status_code == 401:
        response_401 = OAuthErrorResponse.from_dict(response.json())

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
) -> Response[OAuthErrorResponse | OAuthTokenResponse | RestErrorResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: OAuthClientCredentialsRequest | OAuthRefreshTokenRequest,
) -> Response[OAuthErrorResponse | OAuthTokenResponse | RestErrorResponse]:
    """Issue or refresh an access token

     Exchange client credentials (or a refresh token) for a short-lived bearer access token. Accepts both
    grants:

    - `grant_type=client_credentials` — initial authentication. Credentials may be sent via the
    `Authorization: Basic` header (preferred — see [RFC 6749
    §2.3.1](https://datatracker.ietf.org/doc/html/rfc6749#section-2.3.1)) or as `client_id` /
    `client_secret` body fields.
    - `grant_type=refresh_token` — renewal. Returns a new access token AND a new refresh token; the
    previous refresh token is invalidated immediately. Refresh tokens are single-use — any reuse revokes
    every active token for the `client_id` and the partner must re-authenticate via
    `client_credentials`.

    Access tokens live 15 minutes. Refresh tokens live 30 days and are rotated on every use. Rate
    limited to 10 requests per minute per `client_id`.

    Args:
        body (OAuthClientCredentialsRequest | OAuthRefreshTokenRequest): Token request body.
            Discriminated on `grant_type`.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[OAuthErrorResponse | OAuthTokenResponse | RestErrorResponse]
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
    client: AuthenticatedClient,
    body: OAuthClientCredentialsRequest | OAuthRefreshTokenRequest,
) -> OAuthErrorResponse | OAuthTokenResponse | RestErrorResponse | None:
    """Issue or refresh an access token

     Exchange client credentials (or a refresh token) for a short-lived bearer access token. Accepts both
    grants:

    - `grant_type=client_credentials` — initial authentication. Credentials may be sent via the
    `Authorization: Basic` header (preferred — see [RFC 6749
    §2.3.1](https://datatracker.ietf.org/doc/html/rfc6749#section-2.3.1)) or as `client_id` /
    `client_secret` body fields.
    - `grant_type=refresh_token` — renewal. Returns a new access token AND a new refresh token; the
    previous refresh token is invalidated immediately. Refresh tokens are single-use — any reuse revokes
    every active token for the `client_id` and the partner must re-authenticate via
    `client_credentials`.

    Access tokens live 15 minutes. Refresh tokens live 30 days and are rotated on every use. Rate
    limited to 10 requests per minute per `client_id`.

    Args:
        body (OAuthClientCredentialsRequest | OAuthRefreshTokenRequest): Token request body.
            Discriminated on `grant_type`.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        OAuthErrorResponse | OAuthTokenResponse | RestErrorResponse
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: OAuthClientCredentialsRequest | OAuthRefreshTokenRequest,
) -> Response[OAuthErrorResponse | OAuthTokenResponse | RestErrorResponse]:
    """Issue or refresh an access token

     Exchange client credentials (or a refresh token) for a short-lived bearer access token. Accepts both
    grants:

    - `grant_type=client_credentials` — initial authentication. Credentials may be sent via the
    `Authorization: Basic` header (preferred — see [RFC 6749
    §2.3.1](https://datatracker.ietf.org/doc/html/rfc6749#section-2.3.1)) or as `client_id` /
    `client_secret` body fields.
    - `grant_type=refresh_token` — renewal. Returns a new access token AND a new refresh token; the
    previous refresh token is invalidated immediately. Refresh tokens are single-use — any reuse revokes
    every active token for the `client_id` and the partner must re-authenticate via
    `client_credentials`.

    Access tokens live 15 minutes. Refresh tokens live 30 days and are rotated on every use. Rate
    limited to 10 requests per minute per `client_id`.

    Args:
        body (OAuthClientCredentialsRequest | OAuthRefreshTokenRequest): Token request body.
            Discriminated on `grant_type`.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[OAuthErrorResponse | OAuthTokenResponse | RestErrorResponse]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: OAuthClientCredentialsRequest | OAuthRefreshTokenRequest,
) -> OAuthErrorResponse | OAuthTokenResponse | RestErrorResponse | None:
    """Issue or refresh an access token

     Exchange client credentials (or a refresh token) for a short-lived bearer access token. Accepts both
    grants:

    - `grant_type=client_credentials` — initial authentication. Credentials may be sent via the
    `Authorization: Basic` header (preferred — see [RFC 6749
    §2.3.1](https://datatracker.ietf.org/doc/html/rfc6749#section-2.3.1)) or as `client_id` /
    `client_secret` body fields.
    - `grant_type=refresh_token` — renewal. Returns a new access token AND a new refresh token; the
    previous refresh token is invalidated immediately. Refresh tokens are single-use — any reuse revokes
    every active token for the `client_id` and the partner must re-authenticate via
    `client_credentials`.

    Access tokens live 15 minutes. Refresh tokens live 30 days and are rotated on every use. Rate
    limited to 10 requests per minute per `client_id`.

    Args:
        body (OAuthClientCredentialsRequest | OAuthRefreshTokenRequest): Token request body.
            Discriminated on `grant_type`.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        OAuthErrorResponse | OAuthTokenResponse | RestErrorResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed

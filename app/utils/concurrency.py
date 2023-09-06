import typing

import httpx
from httpx import Response, Request


async def send_request(
    client: httpx.AsyncClient, url, http_method, **kwargs
) -> Response:
    http_method = getattr(client, http_method)
    response = await http_method(url, **kwargs)
    return response


class CustomAuth(httpx.Auth):
    def __init__(self, token):
        self.token = token

    def auth_flow(self, request: Request) -> typing.Generator[Request, Response, None]:
        request.headers["Authorization"] = self.token
        yield request


class CustomBasicAuth(httpx.BasicAuth):
    pass

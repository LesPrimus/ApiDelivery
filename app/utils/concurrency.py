import typing

import httpx
from httpx import Response, Request


async def send_request(client: httpx.AsyncClient, url) -> Response:
    response = await client.get(url)
    return response


class CustomAuth(httpx.Auth):
    def __init__(self, token):
        self.token = token

    def auth_flow(self, request: Request) -> typing.Generator[Request, Response, None]:
        request.headers["Authorization"] = self.token
        yield request

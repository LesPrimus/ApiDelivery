import httpx
from httpx import Response


async def send_request(client: httpx.AsyncClient, url) -> Response:
    response = await client.get(url)
    return response

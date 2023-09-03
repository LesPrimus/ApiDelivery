import asyncio
from asyncio import Future

import httpx
from httpx import Response


async def send_request(client: httpx.AsyncClient, url) -> Response:
    response = await client.get(url)
    return response


async def send_batch_requests(nr: int, url: str) -> list[Future]:
    client = httpx.AsyncClient(timeout=40)
    try:
        async with asyncio.TaskGroup() as tg:
            tasks = [tg.create_task(send_request(client, url)) for _ in range(nr)]
        return tasks
    finally:
        await client.aclose()

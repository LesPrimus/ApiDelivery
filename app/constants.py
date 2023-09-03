from enum import StrEnum, unique


@unique
class HttpMethod(StrEnum):
    GET = "GET"
    POST = "POST"
    HEAD = "HEAD"

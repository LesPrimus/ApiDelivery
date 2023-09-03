from enum import StrEnum, unique


@unique
class HttpMethod(StrEnum):
    GET = "GET"
    POST = "POST"
    HEAD = "HEAD"


@unique
class AuthType(StrEnum):
    JWT = "JWT"
    BASIC = "BASIC"

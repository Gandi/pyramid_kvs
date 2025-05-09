from typing import Any, Callable, Mapping, Protocol

from pyramid.interfaces import ISession
from pyramid.response import Response

Settings = Mapping[str, Any]  # shoud be a typed dict

AnyValue = Any


class Request(Protocol):
    session: ISession
    headers: Mapping[str, str]
    cookies: Mapping[str, str]

    def add_response_callback(
        self, callback: Callable[["Request", Response], None]
    ) -> None: ...


class Codec(Protocol):
    def loads(self, data: str) -> AnyValue: ...

    def dumps(self, value: AnyValue) -> str: ...

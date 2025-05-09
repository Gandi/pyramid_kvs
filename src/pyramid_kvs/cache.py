import logging
from typing import Any, List, Mapping, Optional

from pyramid_kvs.typing import Request

from .kvs import KVS
from .serializer import serializer
from .typing import AnyValue

log = logging.getLogger(__name__)


class ApplicationCache:
    """
    An application cache for pyramid
    """

    _client = None

    def __init__(self, request: Request) -> None:
        pass

    def __call__(self, request: Request) -> "ApplicationCache":
        return self

    @classmethod
    def connect(cls, settings: Mapping[str, Any]) -> None:
        """Call that method in the pyramid configuration phase."""
        server = (
            settings["kvs.cache"]
            if isinstance(settings["kvs.cache"], dict)
            else serializer("json").loads(settings["kvs.cache"])
        )
        server.setdefault("key_prefix", "cache::")
        server.setdefault("codec", "json")
        cls._client = KVS(**server)

    @property
    def client(self) -> KVS:
        assert self._client
        return self._client

    def __getitem__(self, key: str) -> AnyValue:
        return self.client.get(key)

    def __setitem__(self, key: str, value: AnyValue) -> None:
        self.client.set(key, value)

    def __delitem__(self, key: str) -> None:
        if key not in self:
            raise KeyError(key)
        self.client.delete(key)

    def __contains__(self, key: str) -> bool:
        return self.client.get(key) is not None

    def get(self, key: str, default: Optional[AnyValue] = None) -> AnyValue:
        return self.client.get(key, default)

    def list_keys(self, pattern: str = "*") -> List[str]:
        return self.client.get_keys(pattern)

    def set(self, key: str, value: AnyValue, ttl: Optional[int] = None) -> None:
        self.client.set(key, value, ttl=ttl)

    def pop(self, key: str, default: Optional[AnyValue] = None) -> AnyValue:
        try:
            data = self.client.get(key, default)
            self.__delitem__(key)
        except KeyError:
            data = default
        return data

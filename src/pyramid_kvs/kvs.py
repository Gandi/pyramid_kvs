from typing import Any, List, Mapping, Optional, Type, Union

from pyramid_kvs.typing import AnyValue

from .serializer import serializer


class KVS:
    """
    Create a Key Value Store connection.
    Redis and Memcache are support.
    """

    def __new__(cls, kvs: str, *args: Any, **kwargs: Any) -> "KVS":
        return object.__new__(_implementations[kvs])

    def __init__(
        self,
        kvs: str,
        kvs_kwargs: Optional[Mapping[str, Any]] = None,
        key_prefix: str = "",
        ttl: int = 3600,
        codec: str = "json",
    ):
        self.key_prefix = key_prefix.encode("utf-8")
        self.ttl = ttl
        self._serializer = serializer(codec)
        # If the codec is not specified in the configuration
        # the codec was pickle, and now it is json, so we have
        # to fallback to the previous serializer
        self._backward_serializer = serializer("pickle")
        kvs_kwargs = kvs_kwargs or {}
        self._client = self._create_client(**kvs_kwargs)

    def get(self, key: str, default: Optional[AnyValue] = None) -> AnyValue:
        if key is None:
            return default
        ret = self.raw_get(key)
        if ret is None:
            return default
        try:
            return self._serializer.loads(ret)
        except Exception:
            return self._backward_serializer.loads(ret)

    def set(self, key: str, value: AnyValue, ttl: Optional[int] = None) -> AnyValue:
        value = self._serializer.dumps(value)
        return self.raw_set(key, value, ttl or self.ttl)

    def _get_key(self, key: Union[str, bytes]) -> bytes:
        if isinstance(key, str):
            key = key.encode("utf-8")
        return self.key_prefix + key

    def get_keys(self, pattern: str) -> List[str]:
        raise NotImplementedError()

    def _create_client(self, **kwargs: Any) -> Any:
        raise NotImplementedError()

    def delete(self, key: str) -> None:
        self._client.delete(self._get_key(key))

    def raw_get(self, key: str, default: Optional[AnyValue] = None) -> AnyValue:
        ret = self._client.get(self._get_key(key))
        return default if ret is None else ret

    def raw_set(self, key: str, value: str, ttl: int) -> None:
        self._client.set(self._get_key(key), value, ttl)


class Redis(KVS):
    def _create_client(self, **kwargs: Any) -> Any:
        import redis

        return redis.Redis(**kwargs)

    def raw_set(self, key: str, value: AnyValue, ttl: int) -> None:
        self._client.setex(self._get_key(key), ttl, value)

    def incr(self, key: str) -> None:
        return self._client.incr(self._get_key(key))

    def get_keys(self, pattern: str = "*") -> list[str]:
        keys = self._client.keys(self._get_key(pattern))
        return [key.replace(self.key_prefix, "") for key in keys]


class _NoCodec:
    def __init__(self, strio: Any, *args: Any, **kwargs: Any) -> None:
        self.strio = strio
        self.persistent_load = None

    def load(self) -> str:
        return self.strio.read()

    def dump(self, data: str) -> None:
        return self.strio.write(data)


class Memcache(KVS):
    def _create_client(self, **kwargs: Any) -> Any:
        import memcache

        return memcache.Client(
            pickler=_NoCodec,  # type: ignore
            unpickler=_NoCodec,  # type: ignore
            **kwargs,
        )


_implementations = {"redis": Redis, "memcache": Memcache}


def register(name: str, impl: Type[KVS]) -> None:
    """Register your own implementation,
    it also override registered implementation without any check.
    """
    _implementations[name] = impl

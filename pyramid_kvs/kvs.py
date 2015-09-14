from __future__ import unicode_literals

import sys

from .serializer import serializer


PY3 = sys.version_info[0] == 3
if PY3:
    unicode = str


class KVS(object):
    """
    Create a Key Value Store connection.
    Redis and Memcache are support.
    """
    def __new__(cls, kvs, *args, **kwargs):
        return object.__new__(_implementations[kvs])

    def __init__(self, kvs,
                 kvs_kwargs=None, key_prefix='', ttl=3600, codec='pickle'):
        self.key_prefix = key_prefix.encode('utf-8')
        self.ttl = ttl
        self._serializer = serializer(codec)
        kvs_kwargs = kvs_kwargs or {}
        self._client = self._create_client(**kvs_kwargs)

    def get(self, key, default=None):
        if key is None:
            return default
        ret = self.raw_get(key)
        if ret is None:
            return default
        return self._serializer.loads(ret)

    def set(self, key, value, ttl=None):
        value = self._serializer.dumps(value)
        return self.raw_set(key, value, ttl or self.ttl)

    def _get_key(self, key):
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        return self.key_prefix + key

    def get_keys(self, pattern):
        raise NotImplementedError()

    def _create_client(self, **kwargs):
        raise NotImplementedError()

    def delete(self, key):
        self._client.delete(self._get_key(key))

    def raw_get(self, key, default=None):
        ret = self._client.get(self._get_key(key))
        return default if ret is None else ret

    def raw_set(self, key, value, ttl):
        self._client.set(self._get_key(key), value, ttl)


class Redis(KVS):

    def _create_client(self, **kwargs):
        import redis
        return redis.Redis(**kwargs)

    def raw_set(self, key, value, ttl):
        self._client.setex(self._get_key(key), value, ttl)

    def incr(self, key):
        return self._client.incr(self._get_key(key))

    def get_keys(self, pattern='*'):
        keys = self._client.keys(self._get_key(pattern))
        return [key.replace(self.key_prefix, '') for key in keys]


class _NoCodec(object):
    def __init__(self, strio, *args, **kwargs):
        self.strio = strio
        self.persistent_load = None

    def load(self):
        return self.strio.read()

    def dump(self, data):
        return self.strio.write(data)


class Memcache(KVS):

    def _create_client(self, **kwargs):
        import memcache
        return memcache.Client(pickler=_NoCodec, unpickler=_NoCodec,
                               **kwargs)


_implementations = {'redis': Redis,
                    'memcache': Memcache
                    }


def register(name, impl):
    """ Register your own implementation,
    it also override registered implementation without any check.
    """
    _implementations[name] = impl

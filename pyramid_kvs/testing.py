from . import kvs


class MockCache(kvs.KVS):
    cached_data = {}
    last_ttl = None

    def _create_client(self, **kwargs):
        return self

    def delete(self, key):
        self.cached_data.pop(self._get_key(key), None)

    def raw_get(self, key, default=None):
        return self.cached_data.get(self._get_key(key), default)

    def raw_set(self, key, value, ttl):
        self.cached_data[self._get_key(key)] = value
        MockCache.last_ttl = ttl

    def incr(self, key):
        value = int(self.cached_data[self._get_key(key)])
        value += 1
        self.cached_data[self._get_key(key)] = str(value)
        return value


def includeme(config):
    kvs.register("mock", MockCache)
    config.include("pyramid_kvs")

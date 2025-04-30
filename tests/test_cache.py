import unittest

from pyramid import testing
from pyramid.events import NewRequest

from pyramid_kvs import serializer, subscribe_cache
from pyramid_kvs.cache import ApplicationCache
from pyramid_kvs.testing import MockCache


class DummyRequest(testing.DummyRequest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        subscribe_cache(NewRequest(self))


class CacheTestCase(unittest.TestCase):
    def setUp(self):
        settings = {
            "kvs.cache": {
                "kvs": "mock",
                "codec": "json",
                "key_prefix": "test::",
                "ttl": 20,
            }
        }
        self.config = testing.setUp(settings=settings)
        self.config.include("pyramid_kvs.testing")

    def tearDown(self):
        testing.tearDown()

    def test_cache(self):
        request = DummyRequest()
        self.assertIsInstance(request.cache, ApplicationCache)
        client = request.cache.client
        self.assertIsInstance(client, MockCache)
        self.assertEqual(client._serializer.dumps, serializer.json.dumps)
        self.assertEqual(client.ttl, 20)
        self.assertEqual(client.key_prefix, b"test::")

    def test_cache_set(self):
        request = DummyRequest()
        request.cache["dummy"] = "value"
        self.assertEqual(MockCache.cached_data[b"test::dummy"], '"value"')
        self.assertEqual(MockCache.last_ttl, 20)

    def test_cache_set_ttl(self):
        request = DummyRequest()
        request.cache.set("dummy", "value", 200)
        self.assertEqual(MockCache.cached_data[b"test::dummy"], '"value"')
        self.assertEqual(MockCache.last_ttl, 200)

    def test_pop_val(self):
        request = DummyRequest()
        MockCache.cached_data[b"test::popme"] = '"value"'
        val = request.cache.pop("popme")
        self.assertEqual(val, "value")
        self.assertNotIn("popme", MockCache.cached_data)

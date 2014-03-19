import unittest
from pyramid import testing
from pyramid.events import NewRequest

from .. import subscribe_cache

from .. import includeme
from ..cache import ApplicationCache
from .. import serializer
from . import MockCache



class DummyRequest(testing.DummyRequest):
    def __init__(self, *args, **kwargs):
        super(DummyRequest, self).__init__(*args, **kwargs)
        subscribe_cache(NewRequest(self))


class CacheTestCase(unittest.TestCase):

    def setUp(self):
        settings = {'kvs.cache': """{"kvs": "mock",
                                     "codec": "json",
                                     "key_prefix": "test::",
                                     "ttl": 20}"""}
        self.config = testing.setUp(settings=settings)
        self.config.include(includeme)

    def test_cache(self):
        request = DummyRequest()
        self.assertIsInstance(request.cache, ApplicationCache)
        client = request.cache.client
        self.assertIsInstance(client, MockCache)
        self.assertEquals(client._serializer.dumps, serializer.json.dumps)
        self.assertEquals(client.ttl, 20)
        self.assertEquals(client.key_prefix, 'test::')

        request.cache['dummy'] = 'value'
        self.assertEquals(MockCache.cached_data['test::dummy'], '"value"')

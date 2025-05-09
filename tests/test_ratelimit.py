import unittest

from pyramid import testing
from pyramid.events import NewRequest

from pyramid_kvs import subscribe_ratelimit
from pyramid_kvs.kvs import KVS
from pyramid_kvs.ratelimit import Ratelimit, RateLimitError
from pyramid_kvs.session import AuthTokenSession
from pyramid_kvs.testing import MockCache


class DummyRequest(testing.DummyRequest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session = AuthTokenSession(
            self, KVS("mock", key_prefix="header::", codec="json"), "X-Dummy-Header"
        )
        subscribe_ratelimit(NewRequest(self))


class RatelimitTestCase(unittest.TestCase):
    def test_ratelimit(self):
        Ratelimit.limit = 10

        MockCache.cached_data = {
            b"header::x-dummy-header::dummy_key": '{"akey": "a val"}',
            b"header::x-dummy-header::dummy_key::ratelimit": "9",
        }
        DummyRequest(headers={"X-Dummy-Header": "dummy_key"})
        rte = MockCache.cached_data[b"header::x-dummy-header::dummy_key::ratelimit"]
        self.assertEqual(rte, "10")
        self.assertRaises(
            RateLimitError, DummyRequest, headers={"X-Dummy-Header": "dummy_key"}
        )

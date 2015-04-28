
from pyramid import testing
from pyramid.events import NewRequest

from .compat import unittest
from .. import subscribe_ratelimit
from ..session import AuthTokenSession
from ..kvs import KVS
from ..ratelimit import Ratelimit, RateLimitError
from ..testing import MockCache


class DummyRequest(testing.DummyRequest):
    def __init__(self, *args, **kwargs):
        super(DummyRequest, self).__init__(*args, **kwargs)
        self.session = AuthTokenSession(self,
                                        KVS('mock', key_prefix='header::',
                                            codec='json'),
                                        'X-Dummy-Header')
        subscribe_ratelimit(NewRequest(self))


class RatelimitTestCase(unittest.TestCase):

    def test_ratelimit(self):
        Ratelimit.limit = 10

        MockCache.cached_data = {
            b'header::x-dummy-header::dummy_key': '{"akey": "a val"}',
            b'header::x-dummy-header::dummy_key::ratelimit': '9'
        }
        DummyRequest(headers={'X-Dummy-Header': 'dummy_key'})
        rte = MockCache.cached_data[b'header::x-dummy-header::dummy_key::ratelimit']
        self.assertEqual(rte, '10')
        self.assertRaises(RateLimitError, DummyRequest,
                          headers={'X-Dummy-Header': 'dummy_key'})

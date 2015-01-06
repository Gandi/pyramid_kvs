from pyramid import testing

from .compat import unittest
from ..session import SessionFactory, AuthTokenSession, CookieSession
from .. import serializer
from . import MockCache


class SessionTestCase(unittest.TestCase):

    def test_authtoken(self):
        settings = {'kvs.session': """{"kvs": "mock",
                                       "key_name": "X-Dummy-Header",
                                       "session_type": "header",
                                       "codec": "json",
                                       "key_prefix": "header::",
                                       "ttl": 20}"""}
        MockCache.cached_data = {b'header::x-dummy-header::dummy_key':
                                     '{"akey": "a val"}'}
        factory = SessionFactory(settings)
        self.assertEqual(factory.session_class, AuthTokenSession)
        request = testing.DummyRequest(headers={'X-Dummy-Header': 'dummy_key'})
        session = factory(request)
        client = session.client
        self.assertIsInstance(client, MockCache)
        self.assertEqual(client._serializer.dumps, serializer.json.dumps)
        self.assertEqual(client.ttl, 20)
        self.assertEqual(client.key_prefix, b'header::')
        self.assertEqual(session['akey'], 'a val')
        self.assertEqual(request.response_callbacks, [session.save_session])

    def test_cookie(self):
        settings = {'kvs.session': """{"kvs": "mock",
                                       "key_name": "SessionId",
                                       "session_type": "cookie",
                                       "codec": "json",
                                       "key_prefix": "cookie::",
                                       "ttl": 20}"""}
        factory = SessionFactory(settings)
        MockCache.cached_data = {
            b'cookie::chocolate': '{"anotherkey": "another val"}'
        }
        self.assertEqual(factory.session_class, CookieSession)
        request = testing.DummyRequest(cookies={'SessionId': 'chocolate'})
        session = factory(request)
        client = session.client
        self.assertIsInstance(client, MockCache)
        self.assertEqual(client._serializer.dumps, serializer.json.dumps)
        self.assertEqual(client.ttl, 20)
        self.assertEqual(client.key_prefix, b'cookie::')
        self.assertEqual(session['anotherkey'], 'another val')
        self.assertEqual(request.response_callbacks, [session.save_session])

    def test_should_renew_session_on_invalidate(self):
        """test that session can be reused just after invalidation
        """
        settings = {'kvs.session': """{"kvs": "mock",
                                       "key_name": "SessionId",
                                       "session_type": "cookie",
                                       "codec": "json",
                                       "key_prefix": "cookie::",
                                       "ttl": 20}"""}
        factory = SessionFactory(settings)
        MockCache.cached_data = {
            b'cookie::chocolate': '{"stuffing": "chocolate"}'
        }
        request = testing.DummyRequest(cookies={'SessionId': 'chocolate'})
        session = factory(request)

        # Ensure session is initialized
        self.assertEqual(session['stuffing'], 'chocolate')
        # Invalidate session
        session.invalidate()
        # session is invalidated
        self.assertFalse('stuffing' in session)
        # ensure it can be reused immediately
        session['stuffing'] = 'macadamia'
        self.assertEqual(session['stuffing'], 'macadamia')

import binascii
import logging
import os
import time
from collections import defaultdict

from pyramid.interfaces import ISession, ISessionFactory
from zope.interface import implementer

from .kvs import KVS
from .serializer import serializer

log = logging.getLogger(__name__)


def _create_token():
    return binascii.hexlify(os.urandom(20))


@implementer(ISession)
class SessionBase:
    def __init__(self, request, client, key_name):
        self._dirty = False
        self.key_name = key_name
        self.client = client
        self.request = request

        self._session_key = self.get_session_key()
        self._session_data = defaultdict(defaultdict)

        if not self._session_key:
            log.warn("No session found")
            return

        stored_data = client.get(self._session_key)
        if stored_data:
            self._session_data.update(stored_data)
        else:
            self.changed()

    # IDict stuff
    def __delitem__(self, key):
        self.changed()
        del self._session_data[key]

    def setdefault(self, key, default=None):
        self.changed()
        return self._session_data.setdefault(key, default)

    def __getitem__(self, key):
        self.changed()
        return self._session_data[key]

    def __contains__(self, key):
        return key in self._session_data

    def __len__(self):
        return len(self._session_data)

    def __repr__(self):
        return self._session_data.__repr__()

    def keys(self):
        return self._session_data.keys()

    def items(self):
        self.changed()
        return self._session_data.items()

    def clear(self):
        self.changed()
        self._session_data.clear()

    def get(self, key, default=None):
        self.changed()
        return self._session_data.get(key, default)

    def __setitem__(self, key, value):
        self.changed()
        return self._session_data.__setitem__(key, value)

    def pop(self, key, default=None):
        self.changed()
        return self._session_data.pop(key, default)

    def update(self, dict_):
        self.changed()
        return self._session_data.update(dict_)

    def __iter__(self):
        self.changed()
        return self._session_data.__iter__()

    def has_key(self, key):
        return key in self._session_data

    def values(self):
        return self._session_data.values()

    def itervalues(self):
        return self._session_data.itervalues()

    def iteritems(self):
        return self._session_data.iteritems()

    def iterkeys(self):
        return self._session_data.iterkeys()

    # ISession Stuff
    def invalidate(self):
        self.changed()
        self._session_data = defaultdict(defaultdict)

    @property
    def created(self):
        return time.time()  # XXX fix me

    def new_csrf_token(self):
        self["__csrf_token"] = _create_token().decode("utf-8")

    def get_csrf_token(self):
        if "__csrf_token" not in self:
            self.new_csrf_token()
        return self["__csrf_token"]

    def peek_flash(self, queue=""):
        return self.get("_f_" + queue, [])

    def pop_flash(self, queue=""):
        return self.pop("_f_" + queue, [])

    def flash(self, msg, queue="", allow_duplicate=True):
        self.changed()
        storage = self.setdefault("_f_" + queue, [])
        if allow_duplicate or (msg not in storage):
            storage.append(msg)

    @property
    def new(self):
        return False

    def changed(self):
        if not self._dirty:
            self._dirty = True
            self.request.add_response_callback(self.save_session)


@implementer(ISession)
class AuthTokenSession(SessionBase):
    def get_session_key(self):
        if not isinstance(self.key_name, (list, tuple)):
            self.key_name = [self.key_name]

        for header in self.key_name:
            if header in self.request.headers:
                return "{}::{}".format(
                    header.lower().replace("_", "-"),
                    self.request.headers[header],
                )

    def update_session_token(self, header_name, value):
        """Create a session from the givent header name"""
        if self._session_key:
            self.client.delete(self._session_key)
        self._session_key = f"{header_name}::{value}"

    def save_session(self, request=None, response=None):
        """Save the session in the key value store, in case a session
        has been found"""
        if not self._session_key:
            return
        if self._session_data is None:  # session invalidated
            self.client.delete(self._session_key)
            return
        self.client.set(self._session_key, self._session_data)


@implementer(ISession)
class CookieSession(SessionBase):
    def get_session_key(self):
        session_key = self.request.cookies.get(self.key_name)
        if not session_key:
            session_key = _create_token()
        return session_key

    def save_session(self, request, response):
        if self._session_data is None:  # session invalidated
            self.client.delete(self._session_key)
            response.delete_cookie(self.key_name)
            return
        response.set_cookie(self.key_name, self._session_key, self.client.ttl)
        self.client.set(self._session_key, self._session_data)


@implementer(ISessionFactory)
class SessionFactory:
    def __init__(self, settings):
        config = serializer("json").loads(settings["kvs.session"])
        config.setdefault("key_prefix", "session::")
        sessions = {
            "header": AuthTokenSession,
            "cookie": CookieSession,
        }

        self.session_class = sessions[config.pop("session_type", "cookie")]
        self.key_name = config.pop("key_name", "session_id")
        self._client = KVS(**config)

    def __call__(self, request):
        return self.session_class(request, self._client, self.key_name)

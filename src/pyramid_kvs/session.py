import binascii
import json
import logging
import os
import time
from collections import defaultdict
from typing import ItemsView, Iterator, KeysView, Mapping, MutableMapping, ValuesView

from pyramid.interfaces import ISession, ISessionFactory
from pyramid.response import Response
from typing_extensions import Optional
from zope.interface import implementer

from pyramid_kvs.typing import AnyValue, Request, Settings

from .kvs import KVS

log = logging.getLogger(__name__)


def _create_token() -> bytes:
    return binascii.hexlify(os.urandom(20))


@implementer(ISession)
class SessionBase:
    def __init__(self, request: Request, client: KVS, key_name: str) -> None:
        self._dirty = False
        self.key_name = key_name
        self.client = client
        self.request = request

        self._session_key = self.get_session_key()
        self._session_data: MutableMapping[str, AnyValue] = defaultdict(defaultdict)

        if not self._session_key:
            log.warn("No session found")
            return

        stored_data = client.get(self._session_key)
        if stored_data:
            self._session_data.update(stored_data)
        else:
            self.changed()

    def get_session_key(self) -> str | None:
        raise NotImplementedError()

    def save_session(self, request: Request, response: Response) -> None:
        raise NotImplementedError()

    # IDict stuff
    def __delitem__(self, key: str) -> None:
        self.changed()
        del self._session_data[key]

    def setdefault(self, key: str, default: AnyValue) -> AnyValue:
        self.changed()
        return self._session_data.setdefault(key, default)

    def __getitem__(self, key: str) -> AnyValue:
        self.changed()
        return self._session_data[key]

    def __contains__(self, key: str) -> bool:
        return key in self._session_data

    def __len__(self) -> int:
        return len(self._session_data)

    def __repr__(self) -> str:
        return self._session_data.__repr__()

    def keys(self) -> KeysView[str]:
        return self._session_data.keys()

    def items(self) -> ItemsView[str, AnyValue]:
        self.changed()
        return self._session_data.items()

    def clear(self) -> None:
        self.changed()
        self._session_data.clear()

    def get(self, key: str, default: Optional[AnyValue] = None) -> AnyValue:
        self.changed()
        return self._session_data.get(key, default)

    def __setitem__(self, key: str, value: AnyValue) -> None:
        self.changed()
        return self._session_data.__setitem__(key, value)

    def pop(self, key: str, default: Optional[AnyValue] = None) -> AnyValue:
        self.changed()
        return self._session_data.pop(key, default)

    def update(self, dict_: Mapping[str, AnyValue]) -> None:
        self.changed()
        self._session_data.update(dict_)

    def __iter__(self) -> Iterator[AnyValue]:
        self.changed()
        return self._session_data.__iter__()

    def has_key(self, key: str) -> bool:
        return key in self._session_data

    def values(self) -> ValuesView[AnyValue]:
        return self._session_data.values()

    # ISession Stuff
    def invalidate(self) -> None:
        self.changed()
        self._session_data = defaultdict(defaultdict)

    @property
    def created(self) -> float:
        return time.time()  # XXX fix me

    def new_csrf_token(self) -> None:
        self["__csrf_token"] = _create_token().decode("utf-8")

    def get_csrf_token(self) -> str:
        if "__csrf_token" not in self:
            self.new_csrf_token()
        return self["__csrf_token"]

    def peek_flash(self, queue: str = "") -> AnyValue:
        return self.get("_f_" + queue, [])

    def pop_flash(self, queue: str = "") -> AnyValue:
        return self.pop("_f_" + queue, [])

    def flash(self, msg: str, queue: str = "", allow_duplicate: bool = True) -> None:
        self.changed()
        storage = self.setdefault("_f_" + queue, [])
        if allow_duplicate or (msg not in storage):
            storage.append(msg)

    @property
    def new(self) -> bool:
        return False

    def changed(self) -> None:
        if not self._dirty:
            self._dirty = True
            self.request.add_response_callback(self.save_session)


@implementer(ISession)
class AuthTokenSession(SessionBase):
    def get_session_key(self) -> str | None:
        if not isinstance(self.key_name, (list, tuple)):
            self.key_name = [self.key_name]  # type: ignore

        for header in self.key_name:
            if header in self.request.headers:
                return "{}::{}".format(
                    header.lower().replace("_", "-"),
                    self.request.headers[header],
                )
        return None

    def update_session_token(self, header_name: str, value: str) -> None:
        """Create a session from the givent header name"""
        if self._session_key:
            self.client.delete(self._session_key)
        self._session_key = f"{header_name}::{value}"

    def save_session(self, request: Request, response: Response) -> None:
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
    def get_session_key(self) -> str | None:
        session_key = self.request.cookies.get(self.key_name)
        if not session_key:
            session_key = _create_token().decode()
        return session_key

    def save_session(self, request: Request, response: Response) -> None:
        assert self._session_key
        if self._session_data is None:  # session invalidated
            self.client.delete(self._session_key)
            response.delete_cookie(self.key_name)
            return
        response.set_cookie(self.key_name, self._session_key, self.client.ttl)
        self.client.set(self._session_key, self._session_data)


@implementer(ISessionFactory)
class SessionFactory:
    def __init__(self, settings: Settings) -> None:
        if isinstance(settings["kvs.session"], dict):
            config = settings["kvs.session"].copy()
        else:
            config = json.loads(settings["kvs.session"])
        config.setdefault("key_prefix", "session::")
        sessions = {
            "header": AuthTokenSession,
            "cookie": CookieSession,
        }

        self.session_class = sessions[config.pop("session_type", "cookie")]
        self.key_name = config.pop("key_name", "session_id")
        self._client = KVS(**config)

    def __call__(self, request: Request) -> SessionBase:
        return self.session_class(request, self._client, self.key_name)

import logging

from .kvs import KVS
from .serializer import serializer

log = logging.getLogger(__name__)


class PerlSession:
    """
    Read only session from a perl storable.
    Use the "connect method" during the configuration to initialize it
    """

    cookie_name = None
    client = None

    def __init__(self, request):
        self._session_key = request.cookies.get(self.cookie_name)

        self.request = request
        self._session_data = self.client.get(self._session_key)
        if self._session_data is None:
            log.warn(f"session {self._session_key} not deserialized")
            self._session_data = {}

    def __call__(self, request):
        return self

    @classmethod
    def connect(cls, settings):
        """Call that method in the pyramid configuration phase."""
        server = serializer("json").loads(settings["kvs.perlsess"])
        server.setdefault("key_prefix", "perlsess::")
        server.setdefault("codec", "storable")
        cls.cookie_name = server.pop("cookie_name", "session_id")
        cls.client = KVS(**server)

    def __getitem__(self, key):
        return self._session_data[key]

    def __len__(self):
        return len(self._session_data)

    def __contains__(self, key):
        return key in self._session_data

    def keys(self):
        return self._session_data.keys()

    def items(self):
        return self._session_data.items()

    def get(self, key, default=None):
        return self._session_data.get(key, default)

    def __iter__(self):
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

    def __repr__(self):
        return self._session_data.__repr__()

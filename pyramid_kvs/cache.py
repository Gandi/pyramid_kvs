import logging

from .serializer import serializer
from .kvs import KVS


log = logging.getLogger(__name__)


class ApplicationCache(object):
    """
    An application cache for pyramid
    """
    client = None

    def __init__(self, request):
        pass

    def __call__(self, request):
        return self

    @classmethod
    def connect(cls, settings):
        """ Call that method in the pyramid configuration phase.
        """
        server = serializer('json').loads(settings['kvs.cache'])
        server.setdefault('key_prefix', 'cache::')
        server.setdefault('codec', 'pickle')
        cls.client = KVS(**server)

    def __getitem__(self, key):
        return self.client.get(key)

    def __setitem__(self, key, value):
        self.client.set(key, value)

    def __delitem__(self, key):
        if key not in self:
            raise KeyError(key)
        return self.client.delete(key)

    def __contains__(self, key):
        return self.client.get(key) is not None

    def get(self, key, default=None):
        return self.client.get(key, default)

    def list_keys(self, pattern='*'):
        return self.client.get_keys(pattern)

    def set(self, key, value, ttl=None):
        self.client.set(key, value, ttl=ttl)

    def pop(self, key, default=None):
        try:
            data = self.client.get(key, default)
            self.__delitem__(key)
        except KeyError:
            pass
        return data

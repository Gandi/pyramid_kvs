
try:
    import cPickle as pickle
except ImportError:
    import pickle

try:
    import simplejson as json
except ImportError:
    import json

try:
    import storable
except ImportError:
    from . import storable


class Storable:
    """Something you probably don't want to use.
    This class is to get the perl storable support as a readable codec."""

    @staticmethod
    def loads(data):
        return storable.thaw(data)

    @staticmethod
    def dumps(data):
        raise NotImplementedError


def serializer(codec):
    """
    Create a serializer that support loads/dumps methods.
    json and pickle are fully supported.
    storable support read only.
    """
    formats = {"json": json, "pickle": pickle, "storable": Storable}
    return formats[codec]

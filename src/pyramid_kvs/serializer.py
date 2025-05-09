try:
    import cPickle as pickle
except ImportError:
    import pickle

try:
    import simplejson as json
except ImportError:
    import json


def serializer(codec):
    """
    Create a serializer that support loads/dumps methods.
    json and pickle are fully supported.
    storable support read only.
    """
    formats = {"json": json, "pickle": pickle}
    return formats[codec]

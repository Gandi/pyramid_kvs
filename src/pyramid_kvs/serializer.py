import json
import pickle

from pyramid_kvs.typing import Codec


def serializer(codec: str) -> Codec:
    """
    Create a serializer that support loads/dumps methods.
    json and pickle are fully supported.
    storable support read only.
    """
    formats = {"json": json, "pickle": pickle}
    return formats[codec]  # type: ignore

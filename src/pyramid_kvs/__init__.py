"""
pyramid_kvs is a Key/Value Store helpers for pyramid.

See the README.rst file for more information.
"""

try:
    from importlib.metadata import version
except ImportError:
    from importlib_metadata import version  # type: ignore

from pyramid.config import Configurator
from pyramid.events import NewRequest

from .cache import ApplicationCache
from .ratelimit import Ratelimit
from .session import SessionFactory

__version__ = version("pyramid-kvs")


def subscribe_ratelimit(event: NewRequest) -> None:
    Ratelimit(event.request)


def includeme(config: Configurator) -> None:
    settings = config.registry.settings  # type: ignore

    if "kvs.cache" in settings:
        ApplicationCache.connect(settings)
        config.add_request_method(ApplicationCache, "cache", property=True)

    if "kvs.session" in settings:
        config.set_session_factory(SessionFactory(settings))

        if "kvs.ratelimit" in settings:
            Ratelimit.configure(settings)
            config.add_subscriber(subscribe_ratelimit, NewRequest)

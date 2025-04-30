"""
pyramid_kvs is a Key/Value Store helpers for pyramid.

See the README.rst file for more information.
"""

__version__ = "1.0.0"

from pyramid.events import NewRequest

from .cache import ApplicationCache
from .perlsess import PerlSession
from .ratelimit import Ratelimit
from .session import SessionFactory


def subscribe_ratelimit(event):
    Ratelimit(event.request)


def includeme(config):
    settings = config.registry.settings

    if "kvs.perlsess" in settings:
        PerlSession.connect(settings)
        config.add_subscriber(PerlSession, "perlsess", property=True)

    if "kvs.cache" in settings:
        ApplicationCache.connect(settings)
        config.add_request_method(ApplicationCache, "cache", property=True)

    if "kvs.session" in settings:
        config.set_session_factory(SessionFactory(settings))

        if "kvs.ratelimit" in settings:
            Ratelimit.configure(settings)
            config.add_subscriber(subscribe_ratelimit, NewRequest)

"""
pyramid_kvs is a Key/Value Store helpers for pyramid.

See the README.rst file for more information.
"""

__version__ = '0.3.0'

from pyramid.events import NewRequest

from .session import SessionFactory
from .perlsess import PerlSession
from .cache import ApplicationCache
from .ratelimit import Ratelimit


def subscribe_perlsess(event):
    request = event.request
    request.set_property(PerlSession(request), 'perlsess', reify=True)


def subscribe_cache(event):
    request = event.request
    request.set_property(ApplicationCache(request), 'cache', reify=True)


def subscribe_ratelimit(event):
    Ratelimit(event.request)


def includeme(config):

    settings = config.registry.settings

    if 'kvs.perlsess' in settings:
        PerlSession.connect(settings)
        config.add_subscriber(subscribe_perlsess, NewRequest)

    if 'kvs.cache' in settings:
        ApplicationCache.connect(settings)
        config.add_subscriber(subscribe_cache, NewRequest)

    if 'kvs.session' in settings:
        config.set_session_factory(SessionFactory(settings))

        if 'kvs.ratelimit' in settings:
            Ratelimit.configure(settings)
            config.add_subscriber(subscribe_ratelimit, NewRequest)

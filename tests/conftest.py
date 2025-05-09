from typing import Any, Iterator, Mapping, Type

import pytest
from pyramid import testing
from pyramid.config import Configurator
from pyramid.interfaces import IRequestExtensions, ISessionFactory
from pyramid.request import apply_request_extensions

from pyramid_kvs.session import SessionFactory
from pyramid_kvs.typing import Request


@pytest.fixture(scope="session")
def settings():
    return {
        "kvs.cache": {
            "kvs": "mock",
            "codec": "json",
            "key_prefix": "test::",
            "ttl": 20,
        },
        "kvs.session": {
            "kvs": "mock",
            "session_type": "header",
            "key_name": "X-Dummy-Header",
            "ttl": 600,
        },
        "kvs.ratelimit": {
            "window": 2,
            "limit": 10,
        },
    }


@pytest.fixture()
def config(settings: Mapping[str, Any]) -> Iterator[Configurator]:
    config = testing.setUp(settings=settings)
    config.include("pyramid_kvs.testing")
    yield config
    testing.tearDown()


@pytest.fixture()
def dummy_request_factory(config: Configurator) -> Type[testing.DummyRequest]:
    class DummyRequest(testing.DummyRequest, Request):
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super().__init__(*args, **kwargs)
            assert config.registry
            exts: IRequestExtensions = config.registry.queryUtility(IRequestExtensions)
            apply_request_extensions(self, exts)
            sess: SessionFactory = config.registry.queryUtility(ISessionFactory)
            self.session = sess(self)

    return DummyRequest


@pytest.fixture()
def dummy_request(
    config: Configurator, dummy_request_factory: Type[testing.DummyRequest]
) -> testing.DummyRequest:
    return dummy_request_factory()

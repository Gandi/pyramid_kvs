import warnings

warnings.warn('importing pyramid_kvs.tests.mock is deprecated, use '
              'pyramid_kvs.testing instead. See README.rst for usage',
              DeprecationWarning)

from pyramid_kvs.testing import MockCache, includeme


class Dummy(object):
    def include(self, *args):
        pass

includeme(Dummy())  # register the mock cache

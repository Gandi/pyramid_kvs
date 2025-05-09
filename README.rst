===========
pyramid_kvs
===========

.. image:: https://github.com/mardiros/pyramid-kvs2/actions/workflows/tests.yml/badge.svg
    :target: https://github.com/mardiros/pyramid-kvs2/actions/workflows/tests.yml

Some Key Value Store basics for pyramid:

Two KVS are implemented:
 - memcache
 - redis

Here are the provides features:

 - An application cache, shared by every request.
 - A session manager
 - A rate limit per session holder

Every of this components are optional, they exists if they are set in the
configuration like below.
Component settings are written in json.

Cache
=====

The application cache is a new attribute of the session. ``request.cache`` if
the settings ``kvs.cache`` exists.
Here are an example of configuration

::

    kvs.cache = {"kvs": "redis",
                 "codec": "pickle",
                 "kvs_kwargs": {},
                 "ttl": 300,
                 "key_prefix": "cache::"}

Every kvs, except the type are optional.
The example contains every key with their default values for a redis instance.
The ``kvs_kwargs`` key is passed to the driver to build the client connection.

Session
=======

The session is accessible via "request.session", it's in every pyramid
application.
This is just an implementation for Key Value Store users.

::

    kvs.session = {"kvs": "redis",
                   "key_name": "session_id",
                   "session_type": "cookie",
                    "ttl": 300,
                    "key_prefix": "session::"}


Every kvs, except the type are optional.
The example contains every key with their default values for a redis instance.

You can also create a session for an http header like authentication token,
it's help to create a cache per user in an API. API don't use cookies.

::

    kvs.session = {"kvs": "redis",
                   "key_name": "X-Auth-Token",
                   "session_type": "header",
                    "ttl": 300,
                    "key_prefix": "session::"}


Ratelimit
=========

The ratelimit works only if the kvs.session is used!
Ratelimit is per session hold and limit number of http queries in a defined
period.

::

    kvs.ratelimit = {"window": 1, "limit": 15}

All keys are optional.
The example contains every key with their default values for a redis instance.


If the ratelimit is enabled, every response will be decorated with the
following http headers:

- ``X-RateLimit-Limit``: max queries in the period.
- ``X-RateLimit-Remaining``: current remaining queries in that period.



Usage
=====

Declare the addons in the ``pyramid.includes`` in your config, then
tweak the settings like above.

::

    # development.ini
    [app:main]
    pyramid.includes =
        pyramid_kvs

    # declare the application cache
    # except type, every keys are optional
    # kvs_kwargs for redis is the parameters of the redis.Redis class
    # see: http://redis-py.readthedocs.org/en/latest/
    # for memcache, parameters of the memcache.Client class
    # https://github.com/linsomniac/python-memcached/blob/master/memcache.py#L160
    kvs.cache = {"type": "redis"}

    # declare the session
    kvs.session = {"type": "redis"}

    # Authorize a session holder to do 20 http queries max in 2 seconds.
    kvs.ratelimit = {"window": 2, "limit": 20}


tests
=====

pyramid_kvs have also a 'mock' implementation of a `kvs` used for testing
purpose, register it using the pyramid plugins in your tests:::

::

  pyramid.includes =
      pyramid_kvs.testing

Changelog
=========

0.4.1 (2019-03-12)
------------------

 * Switch default serializer to json
   WARNING: pickle serialize datetime by default, json don't, force the
            serializer to pickle for backward compatibility in case datetime
            are serialized

0.4.0 (2019-02-18)
------------------

 * Fix backward incompatibility of redis 3.x
 * Drop support of redix 2.x branch


0.3.1 (2019-02-22)
------------------

 * Switch default serializer to json
   WARNING: pickle serialize datetime by default, json don't, force the
            serializer to pickle for backward compatibility in case datetime
            are serialized

0.3.0 (2018-03-15)
------------------

 * Don't freeze pyramid version
 * Remove support of python 2.6


0.2.3 (2015-09-14)
------------------

* Add get keys for Redis

0.2.2 (2015-05-29)
------------------

* Bump version for PyPI upload problems
    A file named "pyramid-kvs-0.2.1.tar.gz" already exists for  pyramid-kvs-0.2.1.
    To fix problems with that file you should create a new release.

0.2.1
-----

* Improve testing


0.2
---

* Add python 3 support


0.1.1
-----

* Fix package, files are missing


0.1
---

* Initial version

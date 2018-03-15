import os
import re
import sys

from setuptools import setup, find_packages

PY3 = sys.version_info[0] == 3
here = os.path.abspath(os.path.dirname(__file__))
name = 'pyramid_kvs'

with open(os.path.join(here, 'README.rst')) as readme:
    README = readme.read()
with open(os.path.join(here, 'CHANGES.rst')) as changes:
    CHANGES = changes.read()

with open(os.path.join(here, name, '__init__.py')) as v_file:
    version = re.compile(r".*__version__ = '(.*?)'",
                         re.S).match(v_file.read()).group(1)


requires = ['pyramid', 'redis']


if PY3:
    requires.append('python3-memcached')
else:
    requires.append('python-memcached')

tests_require = ['nose', 'coverage']
if sys.version_info < (2, 7):
    tests_require += ['unittest2']

extras_require = {'test': tests_require}


setup(name=name.replace('_', '-'),
      version=version,
      description='Session and cache for Pyramid',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        ],
      author='Gandi',
      author_email='feedback@gandi.net',
      url='https://github.com/Gandi/pyramid_kvs',
      keywords='web pyramid pylons',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='{0}.tests'.format(name),
      install_requires=requires,
      tests_require=tests_require,
      extras_require=extras_require
      )


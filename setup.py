import os
import re

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))
name = "pyramid_kvs"

with open(os.path.join(here, "README.rst")) as readme:
    README = readme.read()
with open(os.path.join(here, "CHANGES.rst")) as changes:
    CHANGES = changes.read()

with open(os.path.join(here, name, "__init__.py")) as v_file:
    version = re.compile(r'.*__version__ = "(.*?)"', re.S).match(v_file.read()).group(1)


requires = ["pyramid", "redis >= 3.0", "python3-memcached"]


tests_require = ["pytest", "coverage"]

extras_require = {"test": tests_require, "dev": ["black", "isort"]}


setup(
    name=name.replace("_", "-"),
    version=version,
    description="Session and cache for Pyramid",
    long_description=README + "\n\n" + CHANGES,
    long_description_content_type="text/x-rst",
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    author="Gandi",
    author_email="feedback@gandi.net",
    url="https://github.com/Gandi/pyramid_kvs",
    keywords="web pyramid pylons",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    test_suite=f"{name}.tests",
    install_requires=requires,
    tests_require=tests_require,
    extras_require=extras_require,
)

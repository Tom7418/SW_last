#!/usr/bin/env python

import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

long_description = "EMBER local install"

version = "0.1.0"
package_data = {}
setup(
    name="ember",
    version=version,
    description="Endgame Malware BEnchmark for Research",
    long_description=long_description,
    packages=["ember"],
    package_data=package_data,
    author_email="proth@endgame.com")

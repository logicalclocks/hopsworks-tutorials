import os
import imp
from setuptools import setup


__version__ = imp.load_source(
    "version", os.path("version.py")
).__version__


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="on_demand",
    version=__version__,
    python_requires=">=3.7,<3.10",
    install_requires=[
        "geopy",
    ],
)


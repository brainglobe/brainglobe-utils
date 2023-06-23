from importlib.metadata import PackageNotFoundError, version

__author__ = "Adam Tyson"
try:
    __version__ = version("brainglobe-utils")
except PackageNotFoundError:
    # package is not installed
    pass

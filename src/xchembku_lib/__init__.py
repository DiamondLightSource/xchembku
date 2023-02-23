from importlib.metadata import version

__version__ = version("xchembku")
del version

__all__ = ["__version__"]

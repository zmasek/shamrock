"""Shamrock - A Trefle API Integration."""
from .exceptions import ShamrockException
from .shamrock import ENDPOINTS, NAVIGATION, Shamrock

__author__ = "Zlatko Mašek"
__email__ = "<zlatko.masek@gmail.com>"
__version__ = "0.2.0"
__all__ = ["Shamrock", "ENDPOINTS", "NAVIGATION"]

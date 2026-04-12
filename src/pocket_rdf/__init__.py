"""
Pocket RDF — a lightweight RDF toolkit.
"""

from .loader import load_graphs
from .query import execute_query, serialize_results
from .serializer import serialize_graphs
from .validator import execute_validation, serialize_report

__all__ = [
    "load_graphs",
    "serialize_graphs",
    "execute_query",
    "serialize_results",
    "execute_validation",
    "serialize_report",
]

__version__ = "0.3.0"

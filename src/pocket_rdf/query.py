"""
RDF SPARQL Query Module

Provides utilities for executing SPARQL queries against RDF graphs and datasets
and serializing results.

Used by:
- CLI tools
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Union

from rdflib import Dataset, Graph
from rdflib.query import Result

# Mapping output file extensions → rdflib serializer formats
SERIALIZER_FORMATS = {
    ".xml": "xml",
    ".json": "json",
    ".txt": "txt",
    ".csv": "csv",
}


def detect_output_format(filepath: Path) -> Optional[str]:
    """
    Detect suitable RDF serialization format from the file extension.

    Parameters
    ----------
    filepath : Path
        The target output file path.

    Returns
    -------
    Optional[str]
        rdflib-compatible format string, or None if unsupported.
    """
    return SERIALIZER_FORMATS.get(filepath.suffix.lower())


def execute_query(
    rdf_obj: Union[Graph, Dataset],
    queryfile: Path,
) -> Result:
    """
    Execute a SPARQL query against an RDF graph or dataset and return the results.

    Parameters
    ----------
    rdf_obj : Union[Graph, Dataset]
        RDFLib graph or dataset to query.

    query : Path
        Path to the SPARQL query file.

    Returns
    -------
    Result
        The results of the SPARQL query execution.
    """
    try:
        query = queryfile.read_text()
        return rdf_obj.query(query)
    except Exception as error:
        raise ValueError(f"Failed to load SPARQL query from {queryfile}: {error}")


def serialize_results(results: Result, outfile: Path):
    """
    Serialize SPARQL query results to a file.

    Parameters
    ----------
    results : Result
        The results of the SPARQL query execution.

    outfile : Path
        Target file path for serialized results. Format is inferred from extension.
    """
    try:
        outformat = detect_output_format(outfile)
        if outformat is None:
            raise ValueError(f"Unsupported serialization format for file: {outfile}")

        outfile.parent.mkdir(parents=True, exist_ok=True)
        with outfile.open("wb") as outputFile:
            results.serialize(
                destination=outputFile, format=outformat, encoding="utf-8"
            )
    except Exception as error:
        raise ValueError(
            f"Failed to serialize SPARQL query results to {outfile}"
            f"with error:\n {error}"
        )

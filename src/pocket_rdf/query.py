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

# Mapping output file extensions → rdflib serializer formats for SELECT results
SERIALIZER_FORMATS_SELECT = {
    ".xml": "xml",
    ".json": "json",
    ".txt": "txt",
    ".csv": "csv",
}

# Mapping output file extensions → rdflib serializer formats for ASK results
# (rdflib's txt and csv serializers only support SELECT)
SERIALIZER_FORMATS_ASK = {
    ".xml": "xml",
    ".json": "json",
}

# Mapping output file extensions → rdflib serializer formats for CONSTRUCT / DESCRIBE
# results (which produce RDF graphs)
SERIALIZER_FORMATS_CONSTRUCT_DESCRIBE = {
    ".ttl": "turtle",
    ".nt": "nt",
    ".xml": "xml",
    ".rdf": "xml",
    ".jsonld": "json-ld",
    ".json": "json-ld",
    ".trig": "trig",
}


def detect_output_format(filepath: Path, result_type: str = "SELECT") -> Optional[str]:
    """
    Detect suitable serialization format from the file extension.

    Parameters
    ----------
    filepath : Path
        The target output file path.

    result_type : str
        The SPARQL result type: "SELECT", "ASK", "CONSTRUCT", or "DESCRIBE".

    Returns
    -------
    Optional[str]
        rdflib-compatible format string, or None if unsupported.
    """
    format_map = {
        "SELECT": SERIALIZER_FORMATS_SELECT,
        "ASK": SERIALIZER_FORMATS_ASK,
        "CONSTRUCT": SERIALIZER_FORMATS_CONSTRUCT_DESCRIBE,
        "DESCRIBE": SERIALIZER_FORMATS_CONSTRUCT_DESCRIBE,
    }
    return format_map.get(result_type, {}).get(filepath.suffix.lower())


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

    queryfile : Path
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

    For SELECT/ASK results, uses SPARQL result serializers (xml, json, csv, txt).
    For CONSTRUCT/DESCRIBE results, uses RDF graph serializers (turtle, xml, json-ld,
        etc.).

    Parameters
    ----------
    results : Result
        The results of the SPARQL query execution.

    outfile : Path
        Target file path for serialized results. Format is inferred from extension.
    """
    try:
        result_type = results.type
        is_graph_result = result_type in ("CONSTRUCT", "DESCRIBE")
        outformat = detect_output_format(outfile, result_type)
        if outformat is None:
            raise ValueError(
                f"Unsupported serialization format for file: {outfile} "
                f"for {result_type} results."
            )

        outfile.parent.mkdir(parents=True, exist_ok=True)

        if is_graph_result:
            if results.graph is None:
                raise ValueError(
                    "CONSTRUCT/DESCRIBE query returned no graph to serialize."
                )
            results.graph.serialize(
                destination=outfile, format=outformat, encoding="utf-8"
            )
        else:
            with outfile.open("wb") as outputFile:
                results.serialize(
                    destination=outputFile, format=outformat, encoding="utf-8"
                )
    except Exception as error:
        raise ValueError(
            f"Failed to serialize SPARQL query results to {outfile} "
            f"with error:\n {error}"
        )

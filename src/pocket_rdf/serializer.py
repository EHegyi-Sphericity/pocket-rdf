"""
RDF Serializer Module

Provides utilities for serializing RDF graphs to various formats
based on file extensions.

Used by:
- CLI tools
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Union

from rdflib import Dataset, Graph

# Mapping output file extensions → rdflib serializer formats
SERIALIZER_FORMATS_NAMED_GRAPHS = {
    ".trig": "trig",
    ".nq": "nquads",
    ".txt": "txt",
}


SERIALIZER_FORMATS_DEFAULT_GRAPH = {
    ".ttl": "turtle",
    ".nt": "nt",
    ".xml": "xml",
    ".rdf": "xml",
    ".jsonld": "json-ld",
    ".json": "json-ld",
    ".trig": "trig",
    ".nq": "nquads",
    ".txt": "txt",
}


def detect_output_format(filepath: Path, is_dataset: bool = False) -> Optional[str]:
    """
    Detect suitable RDF serialization format from the file extension.

    Parameters
    ----------
    filepath : Path
        The target output file path.

    is_dataset : bool
        Whether the RDF object to serialize is a dataset with named graphs (True)
            or a single graph (False).

    Returns
    -------
    Optional[str]
        rdflib-compatible format string, or None if unsupported.
    """
    if is_dataset:
        return SERIALIZER_FORMATS_NAMED_GRAPHS.get(filepath.suffix.lower())
    else:
        return SERIALIZER_FORMATS_DEFAULT_GRAPH.get(filepath.suffix.lower())


def serialize_graphs(
    rdf_obj: Union[Graph, Dataset],
    outfile: Path,
) -> None:
    """
    Serialize a single RDF graph to a file.

    Parameters
    ----------
    rdf_obj : Union[Graph, Dataset]
        RDFLib graph or dataset to serialize.

    outfile : Path
        Target file path. Format is inferred from extension.

    Raises
    ------
    ValueError
        If no suitable serialization format can be determined.
    """
    try:
        is_dataset = isinstance(rdf_obj, Dataset)
        outFormat = detect_output_format(outfile, is_dataset)
        if outFormat is None:
            fmt_map = (
                SERIALIZER_FORMATS_NAMED_GRAPHS
                if is_dataset
                else SERIALIZER_FORMATS_DEFAULT_GRAPH
            )
            supported = ", ".join(sorted(fmt_map.keys()))
            mode_label = "named graphs" if is_dataset else "default graph"
            raise ValueError(
                f"Unsupported serialization format for file: {outfile} "
                f"for {mode_label} mode. "
                f"Supported extensions: {supported}"
            )

        outfile.parent.mkdir(parents=True, exist_ok=True)
        if outFormat == "txt":
            with outfile.open("w", encoding="utf-8") as outputFile:
                for statement in rdf_obj:
                    outputFile.write(str(tuple(statement)) + "\n")
        else:
            rdf_obj.serialize(destination=outfile, format=outFormat, encoding="utf-8")
    except Exception as error:
        raise ValueError(
            f"Failed to serialize RDF graph to {outfile} with error:\n {error}"
        )

"""
RDF SHACL Validation Module

Provides utilities for executing SHACL validation on RDF graphs and datasets,
and serializing validation reports.

Used by:
- CLI tools
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Union

from pyshacl import validate
from pyshacl.errors import ValidationFailure
from rdflib import Dataset, Graph, URIRef

# Mapping output file extensions → rdflib serializer formats
SERIALIZER_FORMATS = {
    ".ttl": "turtle",
    ".nt": "nt",
    ".xml": "xml",
    ".rdf": "xml",
    ".jsonld": "json-ld",
    ".json": "json-ld",
    ".trig": "trig",
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


def execute_validation(
    rdf_obj: Union[Graph, Dataset],
    shapesfile: Path,
) -> dict[str, Union[bool, str | URIRef | bool | Graph | ValidationFailure | bytes]]:
    """
    Execute SHACL validation on an RDF graph or dataset against a SHACL shapes file.

    Parameters
    ----------
    rdf_obj : Union[Graph, Dataset]
        RDFLib graph or dataset to validate.

    shapesfile : Path
        Path to the SHACL shapes file.

    Returns
    -------
    Dict[str, Union[bool, Graph]]
        A dictionary containing the validation results, including:
        - 'conforms': bool indicating if the data conforms to the shapes.
        - 'report_graph': Graph containing the validation report details.
    """
    try:
        shapes_graph = Graph().parse(shapesfile)
        conforms, report_graph, _ = validate(
            data_graph=rdf_obj,
            shacl_graph=shapes_graph,
            inference="none",
            advanced=True,
            iterate_rules=True,
            debug=False,
        )
        return {"conforms": conforms, "report_graph": report_graph}

    except Exception as error:
        raise RuntimeError(
            f"Failed to execute validation: {shapesfile} with error:\n {error}"
        )


def serialize_report(report_graph: Graph, outfile: Path) -> None:
    """
    Serialize the SHACL validation report graph to a file.

    Parameters
    ----------
    report_graph : Union[str, URIRef, Graph, ValidationFailure, bytes]
        The validation report graph to serialize.

    outputfile : Path
        The target file path to write the serialized report.
    """
    try:
        outformat = detect_output_format(outfile)
        if outformat is None:
            raise ValueError(f"Unsupported serialization format for file: {outfile}")

        outfile.parent.mkdir(parents=True, exist_ok=True)
        with outfile.open("wb") as outputFile:
            report_graph.serialize(
                destination=outputFile, format=outformat, encoding="utf-8"
            )

    except Exception as error:
        raise ValueError(
            f"Failed to serialize SHACL validation report to {outfile} "
            f"with error:\n {error}"
        )

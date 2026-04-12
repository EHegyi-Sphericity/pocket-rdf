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
from rdflib import Dataset, Graph

# Mapping output file extensions → rdflib serializer formats
SERIALIZER_FORMATS = {
    ".ttl": "turtle",
    ".nt": "nt",
    ".xml": "xml",
    ".rdf": "xml",
    ".jsonld": "json-ld",
    ".json": "json-ld",
    ".trig": "trig",
    ".txt": "txt",
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


def get_nodes(graph_data: Graph | Dataset) -> list[str]:
    nodes = []
    if isinstance(graph_data, Dataset):
        for graph in graph_data.graphs():
            for subj in graph.subjects():
                nodes.append(str(subj))
        return nodes

    for subj in graph_data.subjects():
        nodes.append(str(subj))
    return nodes


def execute_validation(
    data_graph: Union[Graph, Dataset],
    shapesfile: Path,
    context_graph: Union[Graph, Dataset, None] = None,
    allow_infos: bool = False,
    allow_warnings: bool = False,
) -> dict[
    str,
    Union[bool, str, Graph],
]:
    """
    Execute SHACL validation on an RDF graph or dataset against a SHACL shapes file.

    Parameters
    ----------
    data_graph : Union[Graph, Dataset]
        RDFLib graph or dataset to validate.

    shapesfile : Path
        Path to the SHACL shapes file.

    context_graph : Optional[Union[Graph, Dataset]], optional
        Additional RDF graph or dataset to include as context during validation,
        by default None.

    allow_infos : bool, optional
        Shapes marked with severity of sh:Info will not cause result to be invalid.
        By default False.

    allow_warnings : bool, optional
        Shapes marked with severity of sh:Warning or sh:Info will not cause result to
        be invalid. By default False.

    Returns
    -------
    dict[str, Union[bool, Graph, str]]
        A dictionary containing the validation results, including:
        - 'conforms': bool indicating if the data conforms to the shapes.
        - 'report_graph': Graph containing the validation report details.
        - 'report_text': str containing the validation report text.
    """
    focus_nodes = None
    if context_graph is not None:
        focus_nodes = get_nodes(data_graph)
        data_graph += context_graph
    try:
        conforms, report_graph, report_text = validate(
            data_graph=data_graph,
            shacl_graph=shapesfile.resolve().as_uri(),
            inference="none",
            # advanced=True,
            # iterate_rules=True,
            allow_infos=allow_infos,
            allow_warnings=allow_warnings,
            focus_nodes=focus_nodes,
            debug=False,
            # multi_data_graphs_mode="validate_each",
        )
        if not isinstance(report_graph, Graph):
            raise ValueError("Validation report is not a valid RDF graph.")
        if not isinstance(report_text, str):
            raise ValueError("Validation report text is not a valid string.")
        return {
            "conforms": conforms,
            "report_graph": report_graph,
            "report_text": report_text,
        }

    except Exception as error:
        raise RuntimeError(f"Failed to execute validation with error:\n {error}")


def serialize_report(report_graph: Graph, report_text: str, outfile: Path) -> None:
    """
    Serialize the SHACL validation report graph to a file.

    Parameters
    ----------
    report_graph : Graph
        The validation report graph to serialize.

    report_text : str
        The validation report text to serialize.

    outfile : Path
        The target file path to write the serialized report.
    """
    try:
        outformat = detect_output_format(outfile)
        if outformat is None:
            supported = ", ".join(sorted(SERIALIZER_FORMATS.keys()))
            raise ValueError(
                f"Unsupported serialization format for file: {outfile}. "
                f"Supported extensions: {supported}"
            )
        elif outformat == "txt":
            # Special handling for plain text output
            with outfile.open("w", encoding="utf-8") as outputFile:
                outputFile.write(str(report_text))
            return

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

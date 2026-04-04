"""
RDF Loader Module

Provides utilities for loading RDF data from one or more files into either
a single unified RDF graph or a dictionary of separate graphs.

Used by:
- serializer.py
- query.py
- shacl.py
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Union

from rdflib import Dataset, Graph

SUPPORTED_FORMATS = {
    ".ttl": "turtle",
    ".nt": "nt",
    ".xml": "xml",
    ".rdf": "xml",
    ".json": "json-ld",
    ".jsonld": "json-ld",
    ".trig": "trig",
    ".nq": "nquads",
}


def detect_format(filepath: Path) -> Optional[str]:
    """
    Detect RDF serialization format based on file extension.

    Parameters
    ----------
    filepath : Path
        The path to the RDF file.

    Returns
    -------
    Optional[str]
        The rdflib-compatible format string, or None if unsupported.
    """
    return SUPPORTED_FORMATS.get(filepath.suffix.lower())


def assert_supported_format(filepath: Path) -> None:
    """
    Assert that the file is in a supported RDF format.

    Parameters
    ----------
    filepath : Path
        The path to the RDF file.

    Raises
    ------
    ValueError
        If the file does not exist or if the format is unsupported.
    """
    if not filepath.is_file():
        raise ValueError(f"File not found: {filepath}")
    if detect_format(filepath) is None:
        raise ValueError(f"Unsupported RDF format for file: {filepath}")


def load_graphs(
    files: list[Path],
    use_dataset: bool = False,
) -> Union[
    tuple[Graph, list[tuple[Path, str]]], tuple[Dataset, list[tuple[Path, str]]]
]:
    """
    Load multiple RDF files into RDFLib graphs.

    Parameters
    ----------
    files : List[Path]
        Paths to RDF files to load.

    use_dataset : bool
        If True, load each file into a separate named graph within a Dataset.
        If False, unify all files into a single Graph.

    Returns
    -------
    Union[tuple[Graph, List], tuple[Dataset, List]]
        If use_dataset=True → (Dataset with separate named graphs,
            list of failed files).
        If use_dataset=False → (unified Graph, list of failed files).
        Each failed file entry is a tuple of (filepath, error_message).
    """
    failedFiles: list[tuple[Path, str]] = []
    if use_dataset:
        # Return separate named graphs in a Dataset
        dataset = Dataset()
        for file in files:
            try:
                assert_supported_format(file)

                graphName = file.resolve().as_uri()
                dataGraph = dataset.get_context(graphName)
                dataGraph.parse(file, publicID="urn:uuid:")

            except Exception as error:
                failedFiles.append((file, str(error)))

        return dataset, failedFiles

    # Return unified graph
    unified_graph = Graph()
    for file in files:
        try:
            assert_supported_format(file)

            unified_graph.parse(file, publicID="urn:uuid:")

        except Exception as error:
            failedFiles.append((file, str(error)))

    return unified_graph, failedFiles

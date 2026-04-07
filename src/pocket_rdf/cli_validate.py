# pocket_rdf/cli_validate.py

import time
from pathlib import Path
from typing import Annotated

import typer
from rdflib import Graph, URIRef

from .loader import load_graphs
from .validator import execute_validation, serialize_report

SH_RESULT = URIRef("http://www.w3.org/ns/shacl#result")

app = typer.Typer(help="Validate RDF data against SHACL shapes")


def validate(
    datafiles: Annotated[
        list[Path], typer.Argument(help="Input RDF files to validate.")
    ],
    shapesfile: Annotated[
        Path, typer.Option(..., "--shapes", "-s", help="SHACL shapes file.")
    ],
    outfile: Annotated[
        Path,
        typer.Option(..., "--out", "-o", help="Output file for validation report."),
    ],
    use_dataset: bool = typer.Option(
        False, "--dataset", "-d", help="Use dataset for input RDF files."
    ),
):
    """
    Load an RDF file and a SHACL shapes file,
    and validate the RDF data against the shapes.
    """
    datafiles_str = ", ".join(str(f) for f in datafiles)
    typer.echo(f"Loading RDF data from: {datafiles_str}")
    typer.echo(f"...into {'a dataset' if use_dataset else 'a single graph'}")

    t0 = time.perf_counter()
    loaded_graphs = load_graphs(datafiles, use_dataset)
    load_time = time.perf_counter() - t0
    for failed_file, error in loaded_graphs[1]:
        typer.secho(f"Failed to load {failed_file}: {error}", fg=typer.colors.RED)

    graphs = loaded_graphs[0]
    typer.echo(f"Loaded {len(graphs)} triples in {load_time:.3f}s.")

    typer.echo(f"Validating against SHACL shapes from: {shapesfile}")
    t0 = time.perf_counter()
    try:
        validation_report = execute_validation(graphs, shapesfile)
    except Exception as error:
        typer.secho(f"Failed to perform SHACL validation: {error}", fg=typer.colors.RED)
        return
    val_time = time.perf_counter() - t0
    typer.echo(f"Validation completed in {val_time:.3f}s.")

    if not validation_report:
        typer.secho(
            "Validation executed but no report was generated.",
            fg=typer.colors.YELLOW,
        )
        return

    if validation_report["conforms"]:
        typer.secho(
            "Validation successful: Data conforms to SHACL shapes.",
            fg=typer.colors.GREEN,
        )
    else:
        report_graph = validation_report["report_graph"]
        if isinstance(report_graph, Graph):
            violations = len(list(report_graph.triples((None, SH_RESULT, None))))
            typer.secho(
                f"Validation failed: Data does not conform to SHACL shapes. "
                f"{violations} violation(s) found.",
                fg=typer.colors.RED,
            )
        else:
            typer.secho(
                "Validation failed: Data does not conform to SHACL shapes.",
                fg=typer.colors.RED,
            )

    if not isinstance(validation_report["report_graph"], Graph):
        typer.secho(
            "Validation report is not a valid RDF graph. Cannot serialize.",
            fg=typer.colors.RED,
        )
        return

    t0 = time.perf_counter()
    try:
        serialize_report(validation_report["report_graph"], outfile)
        ser_time = time.perf_counter() - t0
        typer.secho(
            f"Validation report serialized to: {outfile}", fg=typer.colors.GREEN
        )
        typer.echo(f"Serialization completed in {ser_time:.3f}s.")
    except Exception as error:
        typer.secho(
            f"Failed to serialize validation report: {error}", fg=typer.colors.RED
        )

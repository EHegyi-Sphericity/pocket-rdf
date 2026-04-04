# pocket_rdf/cli_validate.py

from pathlib import Path
from typing import Annotated

import typer
from rdflib import Graph

from .loader import load_graphs
from .validator import execute_validation, serialize_report

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

    loaded_graphs = load_graphs(datafiles, use_dataset)
    for failed_file, error in loaded_graphs[1]:
        typer.echo(f"Failed to load {failed_file}: {error}")

    graphs = loaded_graphs[0]

    typer.echo(f"Validating against SHACL shapes from: {shapesfile}")
    try:
        validation_report = execute_validation(graphs, shapesfile)
    except Exception as error:
        typer.echo(f"Failed to perform SHACL validation: {error}")
        return

    if not validation_report:
        typer.echo("Validation executed but no report was generated.")
        return

    if validation_report["conforms"]:
        typer.echo("Validation successful: Data conforms to SHACL shapes.")
    else:
        typer.echo("Validation failed: Data does not conform to SHACL shapes.")

    if not isinstance(validation_report["report_graph"], Graph):
        typer.echo("Validation report is not a valid RDF graph. Cannot serialize.")
        return

    try:
        serialize_report(validation_report["report_graph"], outfile)
        typer.echo(f"Validation report serialized to: {outfile}")
    except Exception as error:
        typer.echo(f"Failed to serialize validation report: {error}")

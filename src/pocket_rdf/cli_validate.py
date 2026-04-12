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
    contextfiles: Annotated[
        list[Path] | None,
        typer.Option(
            ...,
            "--context",
            "-c",
            help="Additional RDF files to include as context during validation.",
        ),
    ] = None,
    use_dataset: bool = typer.Option(
        False, "--dataset", "-d", help="Use dataset for input RDF files."
    ),
    allow_infos: bool = typer.Option(
        False,
        "--allow-infos",
        "-i",
        help="Treat sh:Info severity results as non-failing.",
    ),
    allow_warnings: bool = typer.Option(
        False,
        "--allow-warnings",
        "-w",
        help="Treat sh:Warning and sh:Info severity results as non-failing.",
    ),
):
    """
    Load an RDF file and a SHACL shapes file,
    and validate the RDF data against the shapes.
    """
    datafiles_str = ", ".join(str(f) for f in datafiles)
    typer.echo(
        f"\nLoading RDF files into a "
        f"{'dataset' if use_dataset else 'single graph'}: {datafiles_str}"
    )

    t0 = time.perf_counter()
    loaded_graphs = load_graphs(datafiles, use_dataset)
    load_time = time.perf_counter() - t0

    data_graph = loaded_graphs[0]

    typer.secho(
        f"Loaded {len(data_graph)} triples in {load_time:.3f}s.", fg=typer.colors.BLACK
    )

    for failed_file, error in loaded_graphs[1]:
        typer.secho(f"Failed to load {failed_file}: {error}", fg=typer.colors.RED)

    context_graph = None
    if contextfiles:
        contextfiles_str = ", ".join(str(f) for f in contextfiles)
        typer.echo(f"\nLoading additional context RDF files: {contextfiles_str}")

        t0 = time.perf_counter()
        loaded_graphs = load_graphs(contextfiles, use_dataset)
        load_time = time.perf_counter() - t0

        context_graph = loaded_graphs[0]

        typer.secho(
            f"Loaded {len(context_graph)} triples in {load_time:.3f}s.",
            fg=typer.colors.BLACK,
        )

        for failed_file, error in loaded_graphs[1]:
            typer.secho(f"Failed to load {failed_file}: {error}", fg=typer.colors.RED)

    typer.echo(f"\nValidating against SHACL shapes from: {shapesfile}")

    try:
        t0 = time.perf_counter()
        validation_report = execute_validation(
            data_graph, shapesfile, context_graph, allow_infos, allow_warnings
        )
        val_time = time.perf_counter() - t0

        typer.secho(f"Validation completed in {val_time:.3f}s.", fg=typer.colors.BLACK)
    except Exception as error:
        typer.secho(f"Failed to perform SHACL validation: {error}", fg=typer.colors.RED)
        return

    if not validation_report:
        typer.secho(
            "Validation executed but no report was generated.",
            fg=typer.colors.YELLOW,
        )
        return

    conforms = validation_report.get("conforms")
    report_graph = validation_report.get("report_graph")
    report_text = validation_report.get("report_text")

    if (
        isinstance(conforms, bool)
        and isinstance(report_graph, Graph)
        and isinstance(report_text, str)
    ):
        if conforms:
            typer.secho(
                "\nValidation successful: Data conforms to SHACL shapes.",
                fg=typer.colors.GREEN,
            )
        else:
            violations = len(list(report_graph.triples((None, SH_RESULT, None))))
            typer.secho(
                f"\nValidation successful: Data does not conform to SHACL shapes. "
                f"{violations} violation(s) found.",
                fg=typer.colors.YELLOW,
            )
    else:
        typer.secho(
            "Validation report is missing expected keys or has invalid types.",
            fg=typer.colors.RED,
        )
        return

    try:
        t0 = time.perf_counter()
        serialize_report(report_graph, report_text, outfile)
        ser_time = time.perf_counter() - t0

        typer.echo(f"\nValidation report serialized to: {outfile}")
        typer.secho(
            f"Serialization completed in {ser_time:.3f}s.", fg=typer.colors.BLACK
        )
    except Exception as error:
        typer.secho(
            f"\nFailed to serialize validation report: {error}", fg=typer.colors.RED
        )

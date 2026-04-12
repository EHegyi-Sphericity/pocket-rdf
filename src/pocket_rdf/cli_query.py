# pocket_rdf/cli_query.py

import time
from pathlib import Path
from typing import Annotated

import typer

from .loader import load_graphs
from .query import execute_query, serialize_results

app = typer.Typer(help="Run SPARQL queries on RDF data")


def query(
    datafiles: Annotated[list[Path], typer.Argument(help="Input RDF files to query.")],
    queryfile: Annotated[
        Path, typer.Option(..., "--query", "-q", help="SPARQL query file.")
    ],
    outfile: Annotated[
        Path, typer.Option(..., "--out", "-o", help="Output file for query results.")
    ],
    use_dataset: bool = typer.Option(
        False, "--dataset", "-d", help="Use dataset for input RDF files."
    ),
):
    """
    Load an RDF file, execute a SPARQL query, and serialize the results.
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

    typer.echo(f"\nExecuting SPARQL query from: {queryfile}")

    try:
        t0 = time.perf_counter()
        results = execute_query(data_graph, queryfile)
        query_time = time.perf_counter() - t0

        typer.secho(f"Query executed in {query_time:.3f}s.", fg=typer.colors.BLACK)
    except Exception as error:
        typer.secho(f"Failed to execute query: {error}", fg=typer.colors.RED)
        return

    if results.type == "ASK":
        answer = bool(results)
        color = typer.colors.GREEN if answer else typer.colors.YELLOW
        typer.secho(f"\nASK query result: {answer}", fg=color)
    elif results.type == "SELECT":
        typer.secho(
            f"\nSELECT query returned {len(results.bindings)} result(s).",
            fg=typer.colors.GREEN,
        )
    elif results.type in ("CONSTRUCT", "DESCRIBE") and results.graph is not None:
        typer.secho(
            f"\n{results.type} query returned {len(results.graph)} triple(s).",
            fg=typer.colors.GREEN,
        )

    try:
        t0 = time.perf_counter()
        serialize_results(results, outfile)
        ser_time = time.perf_counter() - t0

        typer.echo(f"\nQuery results serialized to: {outfile}")
        typer.secho(
            f"Serialization completed in {ser_time:.3f}s.", fg=typer.colors.BLACK
        )
    except Exception as error:
        typer.secho(
            f"\nFailed to serialize query results: {error}", fg=typer.colors.RED
        )

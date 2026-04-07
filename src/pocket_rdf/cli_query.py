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
    typer.echo(f"Loading RDF data from: {datafiles_str}")
    typer.echo(f"...into {'a dataset' if use_dataset else 'a single graph'}")

    t0 = time.perf_counter()
    loaded_graphs = load_graphs(datafiles, use_dataset)
    load_time = time.perf_counter() - t0
    for failed_file, error in loaded_graphs[1]:
        typer.secho(f"Failed to load {failed_file}: {error}", fg=typer.colors.RED)

    graphs = loaded_graphs[0]
    typer.echo(f"Loaded {len(graphs)} triples in {load_time:.3f}s.")

    typer.echo(f"Executing SPARQL query from: {queryfile}")
    t0 = time.perf_counter()
    try:
        results = execute_query(graphs, queryfile)
    except Exception as error:
        typer.secho(f"Failed to execute query: {error}", fg=typer.colors.RED)
        return
    query_time = time.perf_counter() - t0
    typer.echo(f"Query executed in {query_time:.3f}s.")

    if results.type == "ASK":
        answer = bool(results)
        color = typer.colors.GREEN if answer else typer.colors.YELLOW
        typer.secho(f"ASK query result: {answer}", fg=color)
    elif results.type == "SELECT":
        typer.echo(f"SELECT query returned {len(results.bindings)} result(s).")
    elif results.type in ("CONSTRUCT", "DESCRIBE") and results.graph is not None:
        typer.echo(f"{results.type} query returned {len(results.graph)} triple(s).")

    t0 = time.perf_counter()
    try:
        serialize_results(results, outfile)
        ser_time = time.perf_counter() - t0
        typer.secho(f"Query results serialized to: {outfile}", fg=typer.colors.GREEN)
        typer.echo(f"Serialization completed in {ser_time:.3f}s.")
    except Exception as error:
        typer.secho(f"Failed to serialize query results: {error}", fg=typer.colors.RED)

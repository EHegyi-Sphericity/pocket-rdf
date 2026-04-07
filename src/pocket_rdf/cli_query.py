# pocket_rdf/cli_query.py

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

    loaded_graphs = load_graphs(datafiles, use_dataset)
    for failed_file, error in loaded_graphs[1]:
        typer.secho(f"Failed to load {failed_file}: {error}", fg=typer.colors.RED)

    graphs = loaded_graphs[0]

    typer.echo(f"Executing SPARQL query from: {queryfile}")
    try:
        results = execute_query(graphs, queryfile)
    except Exception as error:
        typer.secho(f"Failed to execute query: {error}", fg=typer.colors.RED)
        return

    if not results:
        typer.secho(
            "Query executed successfully but returned no results.",
            fg=typer.colors.YELLOW,
        )
        return

    try:
        serialize_results(results, outfile)
        typer.secho(f"Query results serialized to: {outfile}", fg=typer.colors.GREEN)
    except Exception as error:
        typer.secho(f"Failed to serialize query results: {error}", fg=typer.colors.RED)

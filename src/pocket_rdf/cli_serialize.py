# pocket_rdf/cli_serialize.py

import time
from pathlib import Path
from typing import Annotated

import typer

from .loader import load_graphs
from .serializer import serialize_graphs

app = typer.Typer(help="Serialize RDF files")


@app.command()
def serialize(
    datafiles: Annotated[
        list[Path], typer.Argument(help="Input RDF files to serialize.")
    ],
    outfile: Annotated[Path, typer.Option(..., "--out", "-o", help="Output RDF file.")],
    use_dataset: bool = typer.Option(
        False, "--dataset", "-d", help="Use dataset for input RDF files."
    ),
):
    """
    Load an RDF file and serialize it into another RDF format.
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

    t0 = time.perf_counter()
    try:
        serialize_graphs(graphs, outfile)
        ser_time = time.perf_counter() - t0
        typer.secho(f"RDF graph serialized to: {outfile}", fg=typer.colors.GREEN)
        typer.echo(f"Serialization completed in {ser_time:.3f}s.")
    except Exception as error:
        typer.secho(f"Failed to serialize RDF graph: {error}", fg=typer.colors.RED)

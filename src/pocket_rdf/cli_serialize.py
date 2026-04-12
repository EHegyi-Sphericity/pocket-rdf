# pocket_rdf/cli_serialize.py

import time
from pathlib import Path
from typing import Annotated

import typer

from .loader import load_graphs
from .serializer import serialize_graphs

app = typer.Typer(help="Serialize RDF files")


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

    try:
        t0 = time.perf_counter()
        serialize_graphs(data_graph, outfile)
        ser_time = time.perf_counter() - t0

        typer.secho(f"\nRDF graph serialized to: {outfile}", fg=typer.colors.GREEN)
        typer.secho(
            f"Serialization completed in {ser_time:.3f}s.", fg=typer.colors.BLACK
        )
    except Exception as error:
        typer.secho(f"\nFailed to serialize RDF graph: {error}", fg=typer.colors.RED)

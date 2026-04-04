# pocket_rdf/cli.py

import typer

from .cli_query import query
from .cli_serialize import serialize
from .cli_validate import validate

app = typer.Typer(help="Pocket RDF command-line tools")

# Add subcommands from the serialize and query modules
app.command()(serialize)
app.command()(query)
app.command()(validate)


def main():
    app()


if __name__ == "__main__":
    main()

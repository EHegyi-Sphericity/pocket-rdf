# pocket-rdf

[![CI](https://github.com/EHegyi-Sphericity/pocket-rdf/actions/workflows/tests.yml/badge.svg)](https://github.com/EHegyi-Sphericity/pocket-rdf/actions/workflows/tests.yml)
[![PyPI](https://img.shields.io/pypi/v/pocket-rdf)](https://pypi.org/project/pocket-rdf/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A lightweight RDF toolkit for Python, providing command-line utilities for loading, serializing, querying, and validating RDF data.

## Features

- **Load RDF Data**: Support for Turtle (`.ttl`), RDF/XML (`.xml`, `.rdf`), JSON-LD (`.json`, `.jsonld`), N-Triples (`.nt`), TriG (`.trig`), and N-Quads (`.nq`)
- **Named Graph Support**: Load each file into its own named graph with `--dataset`, enabling provenance tracking and `GRAPH`-aware SPARQL queries
- **Serialization**: Convert between any supported format; use TriG or N-Quads to preserve named graphs
- **SPARQL Querying**: Execute SPARQL queries on single graphs or datasets
- **SHACL Validation**: Validate RDF data against SHACL shapes (including SPARQL-based constraints)
- **CLI Interface**: Easy-to-use command-line tools built with Typer

## Installation

### Prerequisites

- Python 3.10 or higher

### Install from PyPI

```bash
pip install pocket-rdf
```

### Install from Source

```bash
git clone https://github.com/EHegyi-Sphericity/pocket-rdf.git
cd pocket-rdf
pip install .
```

## Usage

pocket-rdf provides three main commands: `serialize`, `query`, and `validate`.

### Serialize RDF Data

Load and serialize RDF data to different formats.

```bash
pocket-rdf serialize data.ttl --out output.xml
```

Arguments:

- Input RDF files (supports patterns like `*.xml`)

Options:

- `--out`, `-o`: Output file (format inferred from extension)
- `--dataset`, `-d`: Load each input file into its own named graph (enables TriG/N-Quads output)

### Query RDF Data

Execute SPARQL queries on RDF files.

```bash
pocket-rdf query data.ttl --query query.sparql --out results.json
```

Arguments:

- Input RDF files (supports patterns like `*.xml`)

Options:

- `--query`, `-q`: SPARQL query file
- `--out`, `-o`: Output file for results
- `--dataset`, `-d`: Load each input file into its own named graph

### Validate RDF Data

Validate RDF files against SHACL shapes.

```bash
pocket-rdf validate file1.ttl file2.xml --shapes shapes.ttl --out report.ttl
```

Arguments:

- Input RDF files (supports patterns like `*.xml`)

Options:

- `--shapes`, `-s`: SHACL shapes file
- `--out`, `-o`: Output file for validation report
- `--dataset`, `-d`: Load each input file into its own named graph
- `--context`, `-c`: Additional RDF files loaded for reference resolution only (not validated)
- `--allow-infos`: Treat `sh:Info` severity results as non-failing
- `--allow-warnings`: Treat `sh:Warning` and `sh:Info` severity results as non-failing

When a file references entities defined in another file, use `--context` to load
the referenced file for reference resolution without validating it:

```bash
pocket-rdf validate EQ.xml --shapes shapes.ttl --out report.ttl --context EQBD.xml
```

## Examples

The [`examples/`](https://github.com/EHegyi-Sphericity/pocket-rdf/tree/main/examples) directory contains three progressive sets of
working examples, each with its own README, sample data, SPARQL queries, and
SHACL shapes:

| Directory | Scope | Key concepts |
|-----------|-------|--------------|
| [`examples/simple/`](https://github.com/EHegyi-Sphericity/pocket-rdf/tree/main/examples/simple) | Single graph | Load, serialize, query, and validate a small library dataset |
| [`examples/advanced/`](https://github.com/EHegyi-Sphericity/pocket-rdf/tree/main/examples/advanced) | Named graphs (`--dataset`) | Multiple catalogs, `GRAPH` queries, TriG/N-Quads, SPARQL-based SHACL |
| [`examples/cgmes/`](https://github.com/EHegyi-Sphericity/pocket-rdf/tree/main/examples/cgmes) | CGMES power system data | Multi-profile datasets, ENTSO-E SHACL shapes, RDFS-enhanced querying |

## Development

### Running Tests

```bash
python -m pytest tests/
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

Emil Hegyi - EHegyi@sphericity.eu

Project Link: https://github.com/EHegyi-Sphericity/pocket-rdf

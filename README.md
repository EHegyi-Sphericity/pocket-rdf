# pocketRDF

A lightweight RDF toolkit for Python, providing command-line utilities for loading, serializing, querying, and validating RDF data.

## Features

- **Load RDF Data**: Support for multiple RDF formats (Turtle, RDF/XML, JSON-LD, etc.)
- **Serialization**: Export query results in various formats
- **SPARQL Querying**: Execute SPARQL queries on RDF graphs
- **SHACL Validation**: Validate RDF data against SHACL shapes
- **CLI Interface**: Easy-to-use command-line tools built with Typer

## Installation

### Prerequisites

- Python 3.10 or higher

### Install from Source

Clone the repository and install:

```bash
git clone https://github.com/EHegyi-Sphericity/pocket-rdf.git
cd pocket-rdf
pip install .
```

Or install directly from the directory:

```bash
pip install .
```

## Usage

pocketRDF provides three main commands: `serialize`, `query`, and `validate`.

### Serialize RDF Data

Load and serialize RDF data to different formats.

```bash
pocket-rdf serialize data.ttl --out output.xml
```

Arguments:

- Input RDF files (supports patterns like `*.xml`)

Options:

- `--out`, `-o`: Output file (format inferred from extension)
- `--dataset`, `-d`: Use dataset for input RDF files

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
- `--dataset`, `-d`: Use dataset for input RDF files

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
- `--dataset`, `-d`: Use dataset for input RDF files

## Examples

### Serializing to Different Formats

```bash
pocket-rdf serialize \
  input.ttl \
  --out output.jsonld
```

### Querying RDF Data

```bash
pocket-rdf query \
  data.ttl \
  --query count_subjects.sparql \
  --out query_results.txt
```

### Validating CGMES Data

```bash
pocket-rdf validate \
  ../files/*.xml \
  --shapes ../shapes/61970-600-2_Equipment-Simple-SHACL_v2-4-15.ttl \
  --out validation_report.ttl \
  --dataset
```

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

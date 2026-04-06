← [Back to main README](../../README.md) · [Advanced examples](../advanced/) · [CGMES examples](../cgmes/)

# Simple Examples — Single Graph

These examples demonstrate pocket-rdf operations on a **single, unified RDF graph**
(no `--dataset` flag). All triples are loaded into one graph, SPARQL queries use
plain triple patterns (no `GRAPH` keyword), and SHACL shapes validate the graph
directly.

## Prerequisites

### 1. Install pocket-rdf

```bash
pip install .
```

### 2. Navigate to working directory

```
examples\simple
```

## Data

| File | Description |
|------|-------------|
| `data/library.ttl` | A small library with books, authors, and genres — all valid. |
| `data/library_invalid.ttl` | Contains a book without a title and an author without a name — intentionally non-conformant. |

## Queries

| File | Description |
|------|-------------|
| `queries/list_books.sparql` | List all books with their author and genre. |
| `queries/count_books_per_author.sparql` | Count books per author. |
| `queries/books_before_1960.sparql` | Find books published before 1960. |

## Shapes

| File | Description |
|------|-------------|
| `shapes/library_shapes.ttl` | SHACL shapes requiring every Book to have a title, author, and genre, and every Author to have a name. |

---

## 1. Serialize

Convert the Turtle data to other RDF formats.

```bash
# Turtle → RDF/XML
pocket-rdf serialize data/library.ttl --out output/library.xml

# Turtle → JSON-LD
pocket-rdf serialize data/library.ttl --out output/library.jsonld

# Turtle → N-Triples
pocket-rdf serialize data/library.ttl --out output/library.nt
```

The output format is inferred from the file extension.

## 2. Query

Run SPARQL queries against the data.

```bash
# List all books (JSON output)
pocket-rdf query data/library.ttl \
  --query queries/list_books.sparql \
  --out output/list_books.json

# Count books per author (CSV output)
pocket-rdf query data/library.ttl \
  --query queries/count_books_per_author.sparql \
  --out output/books_per_author.csv

# Books before 1960 (plain text output)
pocket-rdf query data/library.ttl \
  --query queries/books_before_1960.sparql \
  --out output/books_before_1960.txt
```

## 3. Validate

Validate data against the SHACL shapes.

### Valid data — should pass

```bash
pocket-rdf validate data/library.ttl \
  --shapes shapes/library_shapes.ttl \
  --out output/validation_pass.ttl
```

Expected output:

```
Validation successful: Data conforms to SHACL shapes.
```

### Invalid data — should fail

```bash
pocket-rdf validate data/library.ttl data/library_invalid.ttl \
  --shapes shapes/library_shapes.ttl \
  --out output/validation_fail.ttl
```

Expected output:

```
Validation failed: Data does not conform to SHACL shapes.
```

The validation report in `output/validation_fail.ttl` will detail which nodes
violated which constraints (missing `ex:title` on a Book, missing `ex:name` on
an Author).

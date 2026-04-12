← [Back to main README](../../README.md) · [Simple examples](../simple/) · [CGMES examples](../cgmes/)

# Advanced Examples — Named Graphs (Dataset)

These examples demonstrate pocket-rdf operations using **named graphs** via the
`--dataset` flag. Each input file is loaded into its own named graph inside an
RDF Dataset. This preserves the provenance of each file and enables SPARQL
queries that use the `GRAPH` keyword to distinguish data sources.

## When to Use `--dataset`

Use `--dataset` when you need to:

- Keep data from separate files in distinct named graphs
- Query which graph a triple belongs to (`GRAPH ?g { ... }`)
- Serialize to quad-aware formats (TriG, N-Quads)
- Validate data that originates from multiple independent sources

Without `--dataset`, all files are merged into a single graph and their origin is
lost.

## Prerequisites

### 1. Install pocket-rdf

```bash
pip install .
```

### 2. Navigate to working directory

```
examples\advanced
```

## Data

| File | Description |
|------|-------------|
| `data/catalog_a.ttl` | Fantasy books (Tolkien) — forms one named graph. |
| `data/catalog_b.ttl` | Sci-fi & thriller books (Asimov, le Carré) — forms another named graph. |
| `data/catalog_c_invalid.ttl` | A book without a title and an author without a name — non-conformant. |
| `data/catalog_d_sparql_invalid.ttl` | A book published before its author was born — violates the SPARQL-based constraint. |
| `data/catalog_e_cross_ref.ttl` | Books referencing authors/genres defined in other catalogs — needs `--context`. |
| `data/catalog_f_missing_recommended.ttl` | A book missing optional fields (pages, published year) — demonstrates severity levels. |

## Queries

| File | Description |
|------|-------------|
| `queries/list_books_by_graph.sparql` | List books and show which named graph each belongs to. |
| `queries/count_triples_per_graph.sparql` | Count triples in each named graph. |
| `queries/cross_graph_authors.sparql` | Find authors that appear in more than one catalog. |

## Shapes

| File | Description |
|------|-------------|
| `shapes/library_shapes.ttl` | Same SHACL shapes as the simple examples — works across named graphs. |
| `shapes/library_shapes_sparql.ttl` | SPARQL-based SHACL constraint: a book must not be published before its author was born. |
| `shapes/library_shapes_info.ttl` | `sh:Info` severity: recommends that every book has a page count. |
| `shapes/library_shapes_warning.ttl` | `sh:Warning` severity: warns if a book is missing a publication year. |

---

## 1. Serialize

When using `--dataset`, each file becomes a named graph. Serialize to **TriG** or
**N-Quads** to preserve the graph boundaries.

```bash
# Two catalogs → TriG (human-readable quads)
pocket-rdf serialize data/catalog_a.ttl data/catalog_b.ttl \
  --dataset --out output/catalogs.trig

# Two catalogs → N-Quads
pocket-rdf serialize data/catalog_a.ttl data/catalog_b.ttl \
  --dataset --out output/catalogs.nq
```

> **Note:** Formats like Turtle or RDF/XML cannot represent named graphs. Use
> TriG (`.trig`) or N-Quads (`.nq`) when serializing datasets.

For comparison, serialize both catalogs into a **single merged graph** (without
`--dataset`). All triples are combined and graph boundaries are lost:

```bash
# Two catalogs → single Turtle file (no named graphs)
pocket-rdf serialize data/catalog_a.ttl data/catalog_b.ttl \
  --out output/catalogs_merged.ttl
```

## 2. Query

SPARQL queries can use the `GRAPH` keyword to access individual named graphs.

```bash
# List books showing which catalog (graph) they come from
pocket-rdf query data/catalog_a.ttl data/catalog_b.ttl \
  --dataset \
  --query queries/list_books_by_graph.sparql \
  --out output/books_by_graph.txt

# Count triples per named graph
pocket-rdf query data/catalog_a.ttl data/catalog_b.ttl \
  --dataset \
  --query queries/count_triples_per_graph.sparql \
  --out output/triples_per_graph.csv

# Find authors appearing in multiple catalogs
pocket-rdf query data/catalog_a.ttl data/catalog_b.ttl \
  --dataset \
  --query queries/cross_graph_authors.sparql \
  --out output/cross_graph_authors.json
```

> **Note:** The last query executes successfully but returns no results — each author exists in only one catalog.

## 3. Validate

SHACL validation works across all named graphs in the dataset.

### Valid data — should pass

```bash
pocket-rdf validate data/catalog_a.ttl data/catalog_b.ttl \
  --dataset \
  --shapes shapes/library_shapes.ttl \
  --out output/validation_pass.ttl
```

Expected output:

```
Validation successful: Data conforms to SHACL shapes.
```

### With invalid data — should fail

```bash
pocket-rdf validate data/catalog_a.ttl data/catalog_b.ttl data/catalog_c_invalid.ttl \
  --dataset \
  --shapes shapes/library_shapes.ttl \
  --out output/validation_fail.ttl
```

Expected output:

```
Validation successful: Data does not conform to SHACL shapes.
```

---

## Comparison: Single Graph vs. Dataset

| Aspect | Single graph | Dataset (`--dataset`) |
|--------|-------------|----------------------|
| Loading | All triples merged | Each file → own named graph |
| SPARQL | Plain `?s ?p ?o` patterns | `GRAPH ?g { ?s ?p ?o }` to select by source |
| Serialize formats | Turtle, RDF/XML, JSON-LD, N-Triples, … | TriG, N-Quads |
| Provenance | Lost after merge | Preserved per file |

---

## SPARQL-based SHACL constraint

The `library_shapes_sparql.ttl` shape uses an embedded SPARQL query (`sh:sparql`)
to enforce a cross-entity rule that cannot be expressed with basic SHACL property
constraints: *a book must not be published before its author was born*.

```bash
# Valid data — all books published after their authors were born
pocket-rdf validate data/catalog_a.ttl data/catalog_b.ttl \
  --dataset \
  --shapes shapes/library_shapes_sparql.ttl \
  --out output/sparql_validation_pass.ttl
```

```bash
# Invalid data — catalog_d contains a book published before the author was born
pocket-rdf validate data/catalog_d_sparql_invalid.ttl \
  --dataset \
  --shapes shapes/library_shapes_sparql.ttl \
  --out output/sparql_validation_fail.ttl
```

Expected output:

```
Validation successful: Data does not conform to SHACL shapes.
```

## Context Files (`--context`)

When a file references entities defined in another file (e.g., authors, genres),
validation fails because the referenced instances are missing. Use `--context` to
load additional files for reference resolution without validating them.

### Without context — fails

Catalog E references `ex:author-tolkien` (from catalog A) and `ex:author-asimov`
(from catalog B). Without context, the `sh:class ex:Author` and `sh:class
ex:Genre` constraints fail:

```bash
pocket-rdf validate data/catalog_e_cross_ref.ttl \
  --dataset \
  --shapes shapes/library_shapes.ttl \
  --out output/cross_ref_no_context.ttl
```

Expected output:

```
Validation successful: Data does not conform to SHACL shapes. 4 violation(s) found.
```

### With context — passes

Load catalogs A and B as context so the author and genre references resolve:

```bash
pocket-rdf validate data/catalog_e_cross_ref.ttl \
  --dataset \
  --shapes shapes/library_shapes.ttl \
  --out output/cross_ref_with_context.ttl \
  --context data/catalog_a.ttl \
  --context data/catalog_b.ttl
```

Expected output:

```
Validation successful: Data conforms to SHACL shapes.
```

> **Note:** Only the files listed as positional arguments are validated against
> the SHACL shapes. Files passed via `--context` are loaded for reference
> resolution only.

## Severity Levels (`--allow-infos`, `--allow-warnings`)

SHACL shapes can declare a severity level (`sh:Info`, `sh:Warning`, or the
default `sh:Violation`). By default, all severity levels cause validation to
report non-conformance. Use `--allow-infos` or `--allow-warnings` to treat
lower-severity results as non-failing.

- `--allow-infos` — `sh:Info` results no longer cause `conforms=false`
- `--allow-warnings` — both `sh:Warning` and `sh:Info` results no longer cause
  `conforms=false`

Catalog F contains a book (`"1984"`) that has no `ex:pages` and no
`ex:published` properties.

### `sh:Info` severity

Without `--allow-infos`, the missing page count causes failure:

```bash
pocket-rdf validate data/catalog_f_missing_recommended.ttl \
  --dataset \
  --shapes shapes/library_shapes_info.ttl \
  --out output/info_fail.ttl
```

Expected output:

```
Validation successful: Data does not conform to SHACL shapes. 1 violation(s) found.
```

With `--allow-infos`, the info-level result is suppressed:

```bash
pocket-rdf validate data/catalog_f_missing_recommended.ttl \
  --dataset \
  --shapes shapes/library_shapes_info.ttl \
  --out output/info_pass.ttl \
  --allow-infos
```

Expected output:

```
Validation successful: Data conforms to SHACL shapes.
```

### `sh:Warning` severity

Without `--allow-warnings`, the missing publication year causes failure:

```bash
pocket-rdf validate data/catalog_f_missing_recommended.ttl \
  --dataset \
  --shapes shapes/library_shapes_warning.ttl \
  --out output/warning_fail.ttl
```

Expected output:

```
Validation successful: Data does not conform to SHACL shapes. 1 violation(s) found.
```

With `--allow-warnings`, warning- and info-level results are suppressed:

```bash
pocket-rdf validate data/catalog_f_missing_recommended.ttl \
  --dataset \
  --shapes shapes/library_shapes_warning.ttl \
  --out output/warning_pass.ttl \
  --allow-warnings
```

Expected output:

```
Validation successful: Data conforms to SHACL shapes.
```

# Advanced Examples — Named Graphs (Dataset)

These examples demonstrate pocketRDF operations using **named graphs** via the
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

## Data

| File | Description |
|------|-------------|
| `data/catalog_a.ttl` | Fantasy books (Tolkien) — forms one named graph. |
| `data/catalog_b.ttl` | Sci-fi & thriller books (Asimov, le Carré) — forms another named graph. |
| `data/catalog_c_invalid.ttl` | A book without a title and an author without a name — non-conformant. |

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
Validation failed: Data does not conform to SHACL shapes.
```

## Comparison: Single Graph vs. Dataset

| Aspect | Single graph | Dataset (`--dataset`) |
|--------|-------------|----------------------|
| Loading | All triples merged | Each file → own named graph |
| SPARQL | Plain `?s ?p ?o` patterns | `GRAPH ?g { ?s ?p ?o }` to select by source |
| Serialize formats | Turtle, RDF/XML, JSON-LD, N-Triples, … | TriG, N-Quads |
| Provenance | Lost after merge | Preserved per file |

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [0.3.0] - 2026-04-12

### Added

- SHACL validation context support via `--context` / `-c` (multiple files) for cross-file reference resolution
- Validation severity controls:
	- `--allow-infos` to treat `sh:Info` as non-failing
	- `--allow-warnings` to treat `sh:Warning` and `sh:Info` as non-failing
- Plain-text SHACL validation report output (`.txt`) in addition to RDF serialization formats
- Advanced examples for cross-catalog references and severity-level validation behavior (`sh:Info`, `sh:Warning`)
- Expanded CGMES and advanced documentation for context-driven validation workflows

### Fixed

- Context-assisted validation now keeps focus on nodes from target input data, reducing false violations from context-only entities
- Documentation links and example references updated

### Changed

- Improved CLI output messages and progress reporting in `query`, `serialize`, and `validate` commands
- Expanded integration and CLI tests for context validation, severity flags, and example workflows

## [0.2.0] - 2026-04-07

### Added

- Full support for ASK, CONSTRUCT, and DESCRIBE SPARQL query types
- Per-query-type serialization format maps (SELECT, ASK, CONSTRUCT/DESCRIBE)
- Colored CLI output for success, error, and warning messages
- Performance statistics: load time, query time, serialization time, triple counts, result counts, violation counts
- Supported file extensions listed in error messages for query, serializer, and validator
- Example SPARQL queries: ASK (`has_fantasy_books.sparql`), DESCRIBE (`describe_tolkien.sparql`), CONSTRUCT (`books_with_authors.sparql`)

### Fixed

- ASK queries no longer crash with `.txt` or `.csv` output formats (unsupported formats now raise clear errors)
- ASK `False` results no longer trigger a false "no results" early return
- Deprecated rdflib API usage: `get_context()` replaced with `graph()`
- Type checker warning: `"bool" is not iterable` for CONSTRUCT/DESCRIBE results

### Changed

- Extracted `SERIALIZER_FORMATS_BY_RESULT_TYPE` module-level constant to eliminate duplication
- Removed redundant empty-results early return guard in CLI query command

## [0.1.0] - 2026-04-06

### Added

- CLI with three commands: `serialize`, `query`, `validate`
- RDF loading from Turtle, RDF/XML, JSON-LD, N-Triples, TriG, and N-Quads
- Named graph support via `--dataset` flag
- SPARQL query execution with JSON, CSV, and plain text output
- SHACL validation (including SPARQL-based constraints)
- Examples: simple (single graph), advanced (named graphs), CGMES (power system)
- CI with GitHub Actions (lint + test matrix for Python 3.10–3.12)
- Pre-commit hooks for formatting and basic checks

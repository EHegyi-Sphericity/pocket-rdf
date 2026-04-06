# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

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

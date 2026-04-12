"""Integration tests for examples/simple — single-graph operations."""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from pocket_rdf.cli import app

SIMPLE = Path(__file__).resolve().parent.parent / "examples" / "simple"
runner = CliRunner()


# ── Serialize ────────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "ext",
    [".xml", ".jsonld", ".nt"],
)
def test_serialize(tmp_path, ext):
    out = tmp_path / f"library{ext}"
    result = runner.invoke(
        app,
        ["serialize", str(SIMPLE / "data" / "library.ttl"), "--out", str(out)],
    )
    assert result.exit_code == 0, result.output
    assert out.exists()
    assert out.stat().st_size > 0


# ── Query ────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "query_file, out_ext",
    [
        ("list_books.sparql", ".json"),
        ("count_books_per_author.sparql", ".csv"),
        ("books_before_1960.sparql", ".txt"),
    ],
)
def test_query(tmp_path, query_file, out_ext):
    out = tmp_path / f"result{out_ext}"
    result = runner.invoke(
        app,
        [
            "query",
            str(SIMPLE / "data" / "library.ttl"),
            "--query",
            str(SIMPLE / "queries" / query_file),
            "--out",
            str(out),
        ],
    )
    assert result.exit_code == 0, result.output
    assert out.exists()
    assert out.stat().st_size > 0


def test_query_ask(tmp_path):
    """ASK query should print the boolean result and serialize to JSON."""
    out = tmp_path / "has_fantasy_books.json"
    result = runner.invoke(
        app,
        [
            "query",
            str(SIMPLE / "data" / "library.ttl"),
            "--query",
            str(SIMPLE / "queries" / "has_fantasy_books.sparql"),
            "--out",
            str(out),
        ],
    )
    assert result.exit_code == 0, result.output
    assert "ASK query result:" in result.output
    assert out.exists()
    assert '"boolean"' in out.read_text()


def test_query_describe(tmp_path):
    """DESCRIBE query should produce RDF output about the requested resource."""
    out = tmp_path / "describe_tolkien.ttl"
    result = runner.invoke(
        app,
        [
            "query",
            str(SIMPLE / "data" / "library.ttl"),
            "--query",
            str(SIMPLE / "queries" / "describe_tolkien.sparql"),
            "--out",
            str(out),
        ],
    )
    assert result.exit_code == 0, result.output
    assert out.exists()
    assert out.stat().st_size > 0


def test_query_construct(tmp_path):
    """CONSTRUCT query should produce a new RDF graph."""
    out = tmp_path / "books_with_authors.ttl"
    result = runner.invoke(
        app,
        [
            "query",
            str(SIMPLE / "data" / "library.ttl"),
            "--query",
            str(SIMPLE / "queries" / "books_with_authors.sparql"),
            "--out",
            str(out),
        ],
    )
    assert result.exit_code == 0, result.output
    assert out.exists()
    content = out.read_text()
    assert "authorName" in content


# ── Validate ─────────────────────────────────────────────────────────────────


def test_validate_pass(tmp_path):
    out = tmp_path / "report.ttl"
    result = runner.invoke(
        app,
        [
            "validate",
            str(SIMPLE / "data" / "library.ttl"),
            "--shapes",
            str(SIMPLE / "shapes" / "library_shapes.ttl"),
            "--out",
            str(out),
        ],
    )
    assert result.exit_code == 0, result.output
    assert "Validation successful" in result.output
    assert "conforms" in result.output
    assert out.exists()


def test_validate_fail(tmp_path):
    out = tmp_path / "report.ttl"
    result = runner.invoke(
        app,
        [
            "validate",
            str(SIMPLE / "data" / "library.ttl"),
            str(SIMPLE / "data" / "library_invalid.ttl"),
            "--shapes",
            str(SIMPLE / "shapes" / "library_shapes.ttl"),
            "--out",
            str(out),
        ],
    )
    assert result.exit_code == 0, result.output
    assert "Validation successful" in result.output
    assert "does not conform" in result.output
    assert out.exists()

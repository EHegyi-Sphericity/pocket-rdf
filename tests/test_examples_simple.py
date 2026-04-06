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
    assert "Validation failed" in result.output
    assert out.exists()

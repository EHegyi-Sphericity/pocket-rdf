"""Integration tests for examples/advanced — named-graph (dataset) operations."""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from pocket_rdf.cli import app

ADVANCED = Path(__file__).resolve().parent.parent / "examples" / "advanced"
DATA = ADVANCED / "data"
runner = CliRunner()

VALID_FILES = [str(DATA / "catalog_a.ttl"), str(DATA / "catalog_b.ttl")]


# ── Serialize ────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("ext", [".trig", ".nq"])
def test_serialize_dataset(tmp_path, ext):
    out = tmp_path / f"catalogs{ext}"
    result = runner.invoke(
        app,
        ["serialize", *VALID_FILES, "--dataset", "--out", str(out)],
    )
    assert result.exit_code == 0, result.output
    assert out.exists()
    assert out.stat().st_size > 0


def test_serialize_merged(tmp_path):
    out = tmp_path / "catalogs_merged.ttl"
    result = runner.invoke(
        app,
        ["serialize", *VALID_FILES, "--out", str(out)],
    )
    assert result.exit_code == 0, result.output
    assert out.exists()
    assert out.stat().st_size > 0


# ── Query ────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "query_file, out_ext",
    [
        ("list_books_by_graph.sparql", ".txt"),
        ("count_triples_per_graph.sparql", ".csv"),
    ],
)
def test_query_dataset(tmp_path, query_file, out_ext):
    out = tmp_path / f"result{out_ext}"
    result = runner.invoke(
        app,
        [
            "query",
            *VALID_FILES,
            "--dataset",
            "--query",
            str(ADVANCED / "queries" / query_file),
            "--out",
            str(out),
        ],
    )
    assert result.exit_code == 0, result.output
    assert out.exists()


def test_query_cross_graph_no_results(tmp_path):
    """cross_graph_authors returns no results — each author is in one catalog only."""
    out = tmp_path / "result.json"
    result = runner.invoke(
        app,
        [
            "query",
            *VALID_FILES,
            "--dataset",
            "--query",
            str(ADVANCED / "queries" / "cross_graph_authors.sparql"),
            "--out",
            str(out),
        ],
    )
    assert result.exit_code == 0, result.output
    assert "no results" in result.output.lower()


# ── Validate ─────────────────────────────────────────────────────────────────


def test_validate_pass(tmp_path):
    out = tmp_path / "report.ttl"
    result = runner.invoke(
        app,
        [
            "validate",
            *VALID_FILES,
            "--dataset",
            "--shapes",
            str(ADVANCED / "shapes" / "library_shapes.ttl"),
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
            *VALID_FILES,
            str(DATA / "catalog_c_invalid.ttl"),
            "--dataset",
            "--shapes",
            str(ADVANCED / "shapes" / "library_shapes.ttl"),
            "--out",
            str(out),
        ],
    )
    assert result.exit_code == 0, result.output
    assert "Validation failed" in result.output
    assert out.exists()


def test_validate_sparql_pass(tmp_path):
    out = tmp_path / "report.ttl"
    result = runner.invoke(
        app,
        [
            "validate",
            *VALID_FILES,
            "--dataset",
            "--shapes",
            str(ADVANCED / "shapes" / "library_shapes_sparql.ttl"),
            "--out",
            str(out),
        ],
    )
    assert result.exit_code == 0, result.output
    assert "Validation successful" in result.output
    assert out.exists()


def test_validate_sparql_fail(tmp_path):
    out = tmp_path / "report.ttl"
    result = runner.invoke(
        app,
        [
            "validate",
            str(DATA / "catalog_d_sparql_invalid.ttl"),
            "--dataset",
            "--shapes",
            str(ADVANCED / "shapes" / "library_shapes_sparql.ttl"),
            "--out",
            str(out),
        ],
    )
    assert result.exit_code == 0, result.output
    assert "Validation failed" in result.output
    assert out.exists()

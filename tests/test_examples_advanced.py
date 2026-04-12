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
    assert "0 result(s)" in result.output


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
    assert "conforms" in result.output
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
    assert "Validation successful" in result.output
    assert "does not conform" in result.output
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
    assert "conforms" in result.output
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
    assert "Validation successful" in result.output
    assert "does not conform" in result.output
    assert out.exists()


# ── Context files (--context) ────────────────────────────────────────────────


def test_validate_cross_ref_without_context(tmp_path):
    """Catalog E references authors from A and B — fails without context."""
    out = tmp_path / "report.ttl"
    result = runner.invoke(
        app,
        [
            "validate",
            str(DATA / "catalog_e_cross_ref.ttl"),
            "--dataset",
            "--shapes",
            str(ADVANCED / "shapes" / "library_shapes.ttl"),
            "--out",
            str(out),
        ],
    )
    assert result.exit_code == 0, result.output
    assert "does not conform" in result.output
    assert out.exists()


def test_validate_cross_ref_with_context(tmp_path):
    """Catalog E passes when catalogs A and B are loaded as context."""
    out = tmp_path / "report.ttl"
    result = runner.invoke(
        app,
        [
            "validate",
            str(DATA / "catalog_e_cross_ref.ttl"),
            "--dataset",
            "--shapes",
            str(ADVANCED / "shapes" / "library_shapes.ttl"),
            "--out",
            str(out),
            "--context",
            str(DATA / "catalog_a.ttl"),
            "--context",
            str(DATA / "catalog_b.ttl"),
        ],
    )
    assert result.exit_code == 0, result.output
    assert "conforms" in result.output
    assert "does not conform" not in result.output
    assert out.exists()


# ── Severity levels (--allow-infos, --allow-warnings) ────────────────────────


def test_validate_info_severity_fails_by_default(tmp_path):
    """Catalog F missing pages — info shape fails without --allow-infos."""
    out = tmp_path / "report.ttl"
    result = runner.invoke(
        app,
        [
            "validate",
            str(DATA / "catalog_f_missing_recommended.ttl"),
            "--dataset",
            "--shapes",
            str(ADVANCED / "shapes" / "library_shapes_info.ttl"),
            "--out",
            str(out),
        ],
    )
    assert result.exit_code == 0, result.output
    assert "does not conform" in result.output


def test_validate_info_severity_passes_with_allow_infos(tmp_path):
    """Catalog F passes with --allow-infos."""
    out = tmp_path / "report.ttl"
    result = runner.invoke(
        app,
        [
            "validate",
            str(DATA / "catalog_f_missing_recommended.ttl"),
            "--dataset",
            "--shapes",
            str(ADVANCED / "shapes" / "library_shapes_info.ttl"),
            "--out",
            str(out),
            "--allow-infos",
        ],
    )
    assert result.exit_code == 0, result.output
    assert "conforms" in result.output
    assert "does not conform" not in result.output


def test_validate_warning_severity_fails_by_default(tmp_path):
    """
    Catalog F missing published year — warning shape failswithout --allow-warnings.
    """
    out = tmp_path / "report.ttl"
    result = runner.invoke(
        app,
        [
            "validate",
            str(DATA / "catalog_f_missing_recommended.ttl"),
            "--dataset",
            "--shapes",
            str(ADVANCED / "shapes" / "library_shapes_warning.ttl"),
            "--out",
            str(out),
        ],
    )
    assert result.exit_code == 0, result.output
    assert "does not conform" in result.output


def test_validate_warning_severity_passes_with_allow_warnings(tmp_path):
    """Catalog F passes with --allow-warnings."""
    out = tmp_path / "report.ttl"
    result = runner.invoke(
        app,
        [
            "validate",
            str(DATA / "catalog_f_missing_recommended.ttl"),
            "--dataset",
            "--shapes",
            str(ADVANCED / "shapes" / "library_shapes_warning.ttl"),
            "--out",
            str(out),
            "--allow-warnings",
        ],
    )
    assert result.exit_code == 0, result.output
    assert "conforms" in result.output
    assert "does not conform" not in result.output


def test_validate_allow_warnings_also_allows_infos(tmp_path):
    """--allow-warnings also suppresses sh:Info results."""
    out = tmp_path / "report.ttl"
    result = runner.invoke(
        app,
        [
            "validate",
            str(DATA / "catalog_f_missing_recommended.ttl"),
            "--dataset",
            "--shapes",
            str(ADVANCED / "shapes" / "library_shapes_info.ttl"),
            "--out",
            str(out),
            "--allow-warnings",
        ],
    )
    assert result.exit_code == 0, result.output
    assert "conforms" in result.output
    assert "does not conform" not in result.output

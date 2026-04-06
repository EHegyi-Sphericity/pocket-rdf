import re
from pathlib import Path

import pytest
from typer.testing import CliRunner

from pocket_rdf.cli import app


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def sample_data_ttl():
    """Load the sample RDF data file in Turtle format."""
    data_file = Path(__file__).parent / "data" / "data.ttl"
    if not data_file.exists():
        pytest.skip(f"Sample data file not found: {data_file}")
    return data_file


@pytest.fixture
def sample_query_sparql():
    """Load the sample SPARQL query file."""
    query_file = Path(__file__).parent / "data" / "query.sparql"
    if not query_file.exists():
        pytest.skip(f"Sample query file not found: {query_file}")
    return query_file


def test_query_to_json(runner, sample_data_ttl, sample_query_sparql, tmp_path):
    """Test SPARQL query with JSON output format."""
    out_file = tmp_path / "results.json"
    result = runner.invoke(
        app,
        [
            "query",
            str(sample_data_ttl),
            "--query",
            str(sample_query_sparql),
            "--out",
            str(out_file),
        ],
    )
    assert result.exit_code == 0
    assert "Query results serialized" in result.output
    assert out_file.exists()
    # Verify the output contains JSON content
    content = out_file.read_text()
    assert "{" in content or "[" in content


def test_query_to_csv(runner, sample_data_ttl, sample_query_sparql, tmp_path):
    """Test SPARQL query with CSV output format."""
    out_file = tmp_path / "results.csv"
    result = runner.invoke(
        app,
        [
            "query",
            str(sample_data_ttl),
            "--query",
            str(sample_query_sparql),
            "--out",
            str(out_file),
        ],
    )
    assert result.exit_code == 0
    assert "Query results serialized" in result.output
    assert out_file.exists()
    # CSV should have content
    content = out_file.read_text()
    assert len(content.strip()) > 0


def test_query_to_xml(runner, sample_data_ttl, sample_query_sparql, tmp_path):
    """Test SPARQL query with XML output format."""
    out_file = tmp_path / "results.xml"
    result = runner.invoke(
        app,
        [
            "query",
            str(sample_data_ttl),
            "--query",
            str(sample_query_sparql),
            "--out",
            str(out_file),
        ],
    )
    assert result.exit_code == 0
    assert "Query results serialized" in result.output
    assert out_file.exists()
    # Verify XML content
    content = out_file.read_text()
    assert "<?xml" in content or "<sparql" in content.lower()


def test_query_to_txt(runner, sample_data_ttl, sample_query_sparql, tmp_path):
    """Test SPARQL query with text output format."""
    out_file = tmp_path / "results.txt"
    result = runner.invoke(
        app,
        [
            "query",
            str(sample_data_ttl),
            "--query",
            str(sample_query_sparql),
            "--out",
            str(out_file),
        ],
    )
    assert result.exit_code == 0
    assert "Query results serialized" in result.output
    assert out_file.exists()


def test_query_to_unsupported_format(
    runner, sample_data_ttl, sample_query_sparql, tmp_path
):
    """Test SPARQL query with unsupported output format."""
    out_file = tmp_path / "results.unsupported"
    result = runner.invoke(
        app,
        [
            "query",
            str(sample_data_ttl),
            "--query",
            str(sample_query_sparql),
            "--out",
            str(out_file),
        ],
    )
    assert result.exit_code == 0
    assert "Failed to serialize SPARQL query results" in result.output
    assert not out_file.exists()


def test_query_missing_data_file(runner, sample_query_sparql, tmp_path):
    """Test query with missing input data file."""
    out_file = tmp_path / "results.json"
    result = runner.invoke(
        app,
        [
            "query",
            "nonexistent.ttl",
            "--query",
            str(sample_query_sparql),
            "--out",
            str(out_file),
        ],
    )
    assert result.exit_code == 0
    assert "Failed to load" in result.output


def test_query_missing_query_file(runner, sample_data_ttl, tmp_path):
    """Test query with missing SPARQL query file."""
    out_file = tmp_path / "results.json"
    result = runner.invoke(
        app,
        [
            "query",
            str(sample_data_ttl),
            "--query",
            "nonexistent.sparql",
            "--out",
            str(out_file),
        ],
    )
    assert result.exit_code == 0
    assert (
        "Failed to execute query" in result.output or "Failed to load" in result.output
    )


def test_query_multiple_files(runner, sample_data_ttl, sample_query_sparql, tmp_path):
    """Test query with multiple input RDF files."""
    out_file = tmp_path / "results.json"
    result = runner.invoke(
        app,
        [
            "query",
            str(sample_data_ttl),
            str(sample_data_ttl),  # Same file twice for testing
            "--query",
            str(sample_query_sparql),
            "--out",
            str(out_file),
        ],
    )
    assert result.exit_code == 0
    assert "Query results serialized" in result.output
    assert out_file.exists()


def test_query_with_dataset_flag(
    runner, sample_data_ttl, sample_query_sparql, tmp_path
):
    """Test query with dataset flag."""
    out_file = tmp_path / "results.json"
    result = runner.invoke(
        app,
        [
            "query",
            str(sample_data_ttl),
            "--query",
            str(sample_query_sparql),
            "--out",
            str(out_file),
            "--dataset",
        ],
    )
    assert result.exit_code == 0
    assert "Query results serialized" in result.output or "Loading RDF" in result.output


def test_query_help(runner):
    """Test query command help."""
    result = runner.invoke(app, ["query", "--help"])
    assert result.exit_code == 0
    clean = re.sub(r"\x1b\[[0-9;]*m", "", result.output)
    assert "--query" in clean
    assert "--out" in clean


def test_query_with_short_options(
    runner, sample_data_ttl, sample_query_sparql, tmp_path
):
    """Test query command with short option names."""
    out_file = tmp_path / "results.json"
    result = runner.invoke(
        app,
        [
            "query",
            str(sample_data_ttl),
            "-q",
            str(sample_query_sparql),
            "-o",
            str(out_file),
        ],
    )
    assert result.exit_code == 0
    assert "Query results serialized" in result.output
    assert out_file.exists()

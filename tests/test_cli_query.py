import re
from pathlib import Path
from unittest.mock import MagicMock, patch

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


@pytest.fixture
def ask_true_query(tmp_path):
    """Create a SPARQL ASK query that matches the test data."""
    query_file = tmp_path / "ask_true.sparql"
    query_file.write_text(
        'PREFIX ex: <http://example.org/>\nASK { ex:subject ex:predicate "object" . }'
    )
    return query_file


@pytest.fixture
def ask_false_query(tmp_path):
    """Create a SPARQL ASK query that does not match the test data."""
    query_file = tmp_path / "ask_false.sparql"
    query_file.write_text(
        "PREFIX ex: <http://example.org/>\nASK { ex:nothing ex:predicate ?o . }"
    )
    return query_file


def test_query_ask_true_prints_result(
    runner, sample_data_ttl, ask_true_query, tmp_path
):
    """ASK query returning True should print the boolean result."""
    out_file = tmp_path / "ask_result.json"
    result = runner.invoke(
        app,
        [
            "query",
            str(sample_data_ttl),
            "-q",
            str(ask_true_query),
            "-o",
            str(out_file),
        ],
    )
    assert result.exit_code == 0
    assert "ASK query result: True" in result.output
    assert "Query results serialized" in result.output


def test_query_ask_false_prints_result(
    runner, sample_data_ttl, ask_false_query, tmp_path
):
    """ASK query returning False should print the boolean result and still serialize."""
    out_file = tmp_path / "ask_result.json"
    result = runner.invoke(
        app,
        [
            "query",
            str(sample_data_ttl),
            "-q",
            str(ask_false_query),
            "-o",
            str(out_file),
        ],
    )
    assert result.exit_code == 0
    assert "ASK query result: False" in result.output
    assert "Query results serialized" in result.output
    assert out_file.exists()


def test_query_ask_txt_unsupported(runner, sample_data_ttl, ask_true_query, tmp_path):
    """ASK query with .txt output should fail with a clear error."""
    out_file = tmp_path / "ask_result.txt"
    result = runner.invoke(
        app,
        [
            "query",
            str(sample_data_ttl),
            "-q",
            str(ask_true_query),
            "-o",
            str(out_file),
        ],
    )
    assert result.exit_code == 0
    assert "ASK query result: True" in result.output
    assert "Failed to serialize" in result.output


@pytest.fixture
def construct_query(tmp_path):
    """Create a SPARQL CONSTRUCT query."""
    query_file = tmp_path / "construct.sparql"
    query_file.write_text(
        "PREFIX ex: <http://example.org/>\n"
        "CONSTRUCT { ?s ex:predicate ?o . }\n"
        "WHERE { ?s ex:predicate ?o . }"
    )
    return query_file


@pytest.fixture
def describe_query(tmp_path):
    """Create a SPARQL DESCRIBE query."""
    query_file = tmp_path / "describe.sparql"
    query_file.write_text("PREFIX ex: <http://example.org/>\n" "DESCRIBE ex:subject")
    return query_file


def test_query_construct(runner, sample_data_ttl, construct_query, tmp_path):
    """CONSTRUCT query should report triple count and serialize to TTL."""
    out_file = tmp_path / "construct_result.ttl"
    result = runner.invoke(
        app,
        [
            "query",
            str(sample_data_ttl),
            "-q",
            str(construct_query),
            "-o",
            str(out_file),
        ],
    )
    assert result.exit_code == 0
    assert "CONSTRUCT query returned" in result.output
    assert "triple(s)" in result.output
    assert "Query results serialized" in result.output
    assert out_file.exists()
    content = out_file.read_text()
    assert len(content.strip()) > 0


def test_query_construct_to_json(runner, sample_data_ttl, construct_query, tmp_path):
    """CONSTRUCT query serialized to JSON-LD."""
    out_file = tmp_path / "construct_result.jsonld"
    result = runner.invoke(
        app,
        [
            "query",
            str(sample_data_ttl),
            "-q",
            str(construct_query),
            "-o",
            str(out_file),
        ],
    )
    assert result.exit_code == 0
    assert "CONSTRUCT query returned" in result.output
    assert out_file.exists()


def test_query_describe(runner, sample_data_ttl, describe_query, tmp_path):
    """DESCRIBE query should report triple count and serialize to TTL."""
    out_file = tmp_path / "describe_result.ttl"
    result = runner.invoke(
        app,
        [
            "query",
            str(sample_data_ttl),
            "-q",
            str(describe_query),
            "-o",
            str(out_file),
        ],
    )
    assert result.exit_code == 0
    assert "DESCRIBE query returned" in result.output
    assert "triple(s)" in result.output
    assert "Query results serialized" in result.output
    assert out_file.exists()
    content = out_file.read_text()
    assert len(content.strip()) > 0


def test_query_construct_unsupported_format(
    runner, sample_data_ttl, construct_query, tmp_path
):
    """CONSTRUCT query with unsupported output format should fail."""
    out_file = tmp_path / "construct_result.csv"
    result = runner.invoke(
        app,
        [
            "query",
            str(sample_data_ttl),
            "-q",
            str(construct_query),
            "-o",
            str(out_file),
        ],
    )
    assert result.exit_code == 0
    assert "Failed to serialize" in result.output


def test_query_construct_with_none_graph(
    runner, sample_data_ttl, construct_query, tmp_path
):
    """CONSTRUCT result with graph=None should skip the triple count message."""
    out_file = tmp_path / "construct_result.ttl"
    mock_result = MagicMock()
    mock_result.type = "CONSTRUCT"
    mock_result.graph = None
    with patch("pocket_rdf.cli_query.execute_query", return_value=mock_result):
        result = runner.invoke(
            app,
            [
                "query",
                str(sample_data_ttl),
                "-q",
                str(construct_query),
                "-o",
                str(out_file),
            ],
        )
    assert result.exit_code == 0
    assert "CONSTRUCT query returned" not in result.output

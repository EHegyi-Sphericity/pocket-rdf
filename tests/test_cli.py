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
def sample_shapes_ttl(tmp_path):
    """Load the sample SHACL shapes file in Turtle format."""
    shapes_file = Path(__file__).parent / "data" / "shapes.ttl"
    if not shapes_file.exists():
        pytest.skip(f"Sample shapes file not found: {shapes_file}")
    return shapes_file


@pytest.fixture
def sample_query_sparql(tmp_path):
    """Load a sample SPARQL query file in SPARQL format."""
    query_file = Path(__file__).parent / "data" / "query.sparql"
    if not query_file.exists():
        pytest.skip(f"Sample query file not found: {query_file}")
    return query_file


def test_validate_success(runner, sample_data_ttl, sample_shapes_ttl, tmp_path):
    """Test successful SHACL validation."""
    out_file = tmp_path / "report.ttl"
    result = runner.invoke(
        app,
        [
            "validate",
            str(sample_data_ttl),
            "--shapes",
            str(sample_shapes_ttl),
            "--out",
            str(out_file),
        ],
    )
    assert result.exit_code == 0
    assert "Validation successful" in result.output
    assert out_file.exists()


def test_validate_failure(runner, sample_data_ttl, tmp_path):
    """Test validation failure with invalid shapes."""
    shapes_file = tmp_path / "bad_shapes.ttl"
    shapes_file.write_text("""@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix ex: <http://example.org/> .

ex:Shape a sh:NodeShape ;
    sh:targetClass ex:Class ;
    sh:property [
        sh:path ex:missing ;
        sh:minCount 2 ;  # This will fail
    ] .""")
    out_file = tmp_path / "report.ttl"
    result = runner.invoke(
        app,
        [
            "validate",
            str(sample_data_ttl),
            "--shapes",
            str(shapes_file),
            "--out",
            str(out_file),
        ],
    )
    assert result.exit_code == 0  # CLI doesn't exit on validation failure
    assert "Validation failed" in result.output


def test_validate_missing_file(runner, tmp_path):
    """Test validation with missing input file."""
    shapes_file = tmp_path / "shapes.ttl"
    shapes_file.write_text("")
    out_file = tmp_path / "report.ttl"
    result = runner.invoke(
        app,
        [
            "validate",
            "nonexistent.ttl",
            "--shapes",
            str(shapes_file),
            "--out",
            str(out_file),
        ],
    )
    assert result.exit_code == 0  # CLI handles errors gracefully
    assert "Failed to load" in result.output


def test_query_success(runner, sample_data_ttl, sample_query_sparql, tmp_path):
    """Test successful SPARQL query execution."""
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


def test_query_missing_file(runner, sample_query_sparql, tmp_path):
    """Test query with missing input file."""
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


def test_serialize_success(runner, sample_data_ttl, tmp_path):
    """Test successful RDF serialization."""
    out_file = tmp_path / "output.xml"
    result = runner.invoke(
        app, ["serialize", str(sample_data_ttl), "--out", str(out_file)]
    )
    assert result.exit_code == 0
    assert "RDF graph serialized" in result.output
    assert out_file.exists()


def test_serialize_missing_file(runner, tmp_path):
    """Test serialization with missing input file."""
    out_file = tmp_path / "output.xml"
    result = runner.invoke(
        app, ["serialize", "nonexistent.ttl", "--out", str(out_file)]
    )
    assert result.exit_code == 0
    assert "Failed to load" in result.output


def test_main_help(runner):
    """Test main app help."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Pocket RDF command‑line tools" in result.output
    assert "validate" in result.output
    assert "query" in result.output
    assert "serialize" in result.output


def test_validate_empty_report_message(runner, tmp_path, monkeypatch):
    """Test validate command when execute_validation returns empty result."""
    from pocket_rdf import cli_validate

    data_file = tmp_path / "data.ttl"
    data_file.write_text('@prefix ex: <http://example.org/> . ex:s ex:p "o" .')

    shapes_file = tmp_path / "shapes.ttl"
    shapes_file.write_text("""@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix ex: <http://example.org/> .

ex:Shape a sh:NodeShape ;
    sh:targetClass ex:Class .
""")

    out_file = tmp_path / "report.ttl"

    monkeypatch.setattr(
        cli_validate, "execute_validation", lambda graphs, shapesfile: {}
    )

    result = runner.invoke(
        app,
        [
            "validate",
            str(data_file),
            "--shapes",
            str(shapes_file),
            "--out",
            str(out_file),
        ],
    )

    assert result.exit_code == 0
    assert "Validation executed but no report was generated." in result.output
    assert not out_file.exists()


def test_validate_report_graph_invalid(runner, tmp_path, monkeypatch):
    """Test validate command when report_graph is not an RDFLib Graph."""
    from pocket_rdf import cli_validate

    data_file = tmp_path / "data.ttl"
    data_file.write_text('@prefix ex: <http://example.org/> . ex:s ex:p "o" .')

    shapes_file = tmp_path / "shapes.ttl"
    shapes_file.write_text("""@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix ex: <http://example.org/> .

ex:Shape a sh:NodeShape ;
    sh:targetClass ex:Class .
""")

    out_file = tmp_path / "report.ttl"

    monkeypatch.setattr(
        cli_validate,
        "execute_validation",
        lambda graphs, shapesfile: {"conforms": True, "report_graph": "not-graph"},
    )

    result = runner.invoke(
        app,
        [
            "validate",
            str(data_file),
            "--shapes",
            str(shapes_file),
            "--out",
            str(out_file),
        ],
    )

    assert result.exit_code == 0
    assert (
        "Validation report is not a valid RDF graph. Cannot serialize." in result.output
    )
    assert not out_file.exists()


def test_main_calls_app(monkeypatch):
    """Test that cli.main() calls app()."""
    import pocket_rdf.cli as cli_module

    called = {"count": 0}

    class FakeApp:
        def __call__(self):
            called["count"] += 1

    fake_app = FakeApp()
    monkeypatch.setattr(cli_module, "app", fake_app)

    cli_module.main()

    assert called["count"] == 1

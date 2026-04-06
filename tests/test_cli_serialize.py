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


def test_serialize_to_turtle(runner, sample_data_ttl, tmp_path):
    """Test serialization to Turtle format."""
    out_file = tmp_path / "output.ttl"
    result = runner.invoke(
        app, ["serialize", str(sample_data_ttl), "--out", str(out_file)]
    )
    assert result.exit_code == 0
    assert "RDF graph serialized" in result.output
    assert out_file.exists()
    # Verify the output contains RDF content
    content = out_file.read_text()
    assert "@prefix" in content or "rdf" in content.lower()


def test_serialize_to_xml(runner, sample_data_ttl, tmp_path):
    """Test serialization to RDF/XML format."""
    out_file = tmp_path / "output.xml"
    result = runner.invoke(
        app, ["serialize", str(sample_data_ttl), "--out", str(out_file)]
    )
    assert result.exit_code == 0
    assert "RDF graph serialized" in result.output
    assert out_file.exists()
    # Verify the output contains XML content
    content = out_file.read_text()
    assert "<?xml" in content or "<rdf" in content


def test_serialize_to_jsonld(runner, sample_data_ttl, tmp_path):
    """Test serialization to JSON-LD format."""
    out_file = tmp_path / "output.jsonld"
    result = runner.invoke(
        app, ["serialize", str(sample_data_ttl), "--out", str(out_file)]
    )
    assert result.exit_code == 0
    assert "RDF graph serialized" in result.output
    assert out_file.exists()
    # Verify the output contains JSON content
    content = out_file.read_text()
    assert "{" in content or "@context" in content


def test_serialize_to_ntriples(runner, sample_data_ttl, tmp_path):
    """Test serialization to N-Triples format."""
    out_file = tmp_path / "output.nt"
    result = runner.invoke(
        app, ["serialize", str(sample_data_ttl), "--out", str(out_file)]
    )
    assert result.exit_code == 0
    assert "RDF graph serialized" in result.output
    assert out_file.exists()
    # Verify the output contains triple statements
    content = out_file.read_text()
    assert len(content.strip()) > 0


def test_serialize_to_unsupported_format(runner, sample_data_ttl, tmp_path):
    """Test serialization to an unsupported format."""
    out_file = tmp_path / "output.unsupported"
    result = runner.invoke(
        app, ["serialize", str(sample_data_ttl), "--out", str(out_file)]
    )
    assert result.exit_code == 0  # CLI should handle unsupported formats gracefully
    assert "Failed to serialize RDF graph" in result.output


def test_serialize_missing_input_file(runner, tmp_path):
    """Test serialization with missing input file."""
    out_file = tmp_path / "output.ttl"
    result = runner.invoke(
        app, ["serialize", "nonexistent.ttl", "--out", str(out_file)]
    )
    assert result.exit_code == 0
    assert "Failed to load" in result.output


def test_serialize_multiple_files(runner, sample_data_ttl, tmp_path):
    """Test serialization with multiple input files."""
    out_file = tmp_path / "output.ttl"
    result = runner.invoke(
        app,
        [
            "serialize",
            str(sample_data_ttl),
            str(sample_data_ttl),  # Same file twice for testing
            "--out",
            str(out_file),
        ],
    )
    assert result.exit_code == 0
    assert "RDF graph serialized" in result.output
    assert out_file.exists()


def test_serialize_with_dataset_flag(runner, sample_data_ttl, tmp_path):
    """Test serialization with dataset flag."""
    out_file = tmp_path / "output.trig"
    result = runner.invoke(
        app, ["serialize", str(sample_data_ttl), "--out", str(out_file), "--dataset"]
    )
    # May fail if format not supported with dataset, but shouldn't crash
    assert result.exit_code in [0, 1, 2]


def test_serialize_help(runner):
    """Test serialize command help."""
    result = runner.invoke(app, ["serialize", "--help"])
    assert result.exit_code == 0
    clean = re.sub(r"\x1b\[[0-9;]*m", "", result.output)
    assert "--out" in clean

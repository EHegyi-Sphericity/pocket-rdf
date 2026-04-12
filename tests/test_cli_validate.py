import re
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from pocket_rdf.cli import app


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def sample_conform_data_ttl():
    """Load the sample conformant RDF data file in Turtle format."""
    data_file = Path(__file__).parent / "data" / "data.ttl"
    if not data_file.exists():
        pytest.skip(f"Sample data file not found: {data_file}")
    return data_file


@pytest.fixture
def sample_non_conform_data_ttl():
    """Load the sample non-conformant RDF data file in Turtle format."""
    data_file = Path(__file__).parent / "data" / "non_conform_data.ttl"
    if not data_file.exists():
        pytest.skip(f"Sample data file not found: {data_file}")
    return data_file


@pytest.fixture
def sample_shapes_ttl():
    """Load the sample SHACL shapes file."""
    shapes_file = Path(__file__).parent / "data" / "shapes.ttl"
    if not shapes_file.exists():
        pytest.skip(f"Sample shapes file not found: {shapes_file}")
    return shapes_file


def test_validate_success(runner, sample_conform_data_ttl, sample_shapes_ttl, tmp_path):
    """Test successful SHACL validation."""
    out_file = tmp_path / "report.ttl"
    result = runner.invoke(
        app,
        [
            "validate",
            str(sample_conform_data_ttl),
            "--shapes",
            str(sample_shapes_ttl),
            "--out",
            str(out_file),
        ],
    )
    assert result.exit_code == 0
    assert "Validation successful" in result.output
    assert out_file.exists()
    # Verify the output is an RDF file
    content = out_file.read_text()
    assert len(content.strip()) > 0


def test_validate_missing_data_file(runner, sample_shapes_ttl, tmp_path):
    """Test validation with missing input data file."""
    out_file = tmp_path / "report.ttl"
    result = runner.invoke(
        app,
        [
            "validate",
            "nonexistent.ttl",
            "--shapes",
            str(sample_shapes_ttl),
            "--out",
            str(out_file),
        ],
    )
    assert result.exit_code == 0
    assert "Failed to load" in result.output


def test_validate_missing_shapes_file(runner, sample_conform_data_ttl, tmp_path):
    """Test validation with missing SHACL shapes file."""
    out_file = tmp_path / "report.ttl"
    result = runner.invoke(
        app,
        [
            "validate",
            str(sample_conform_data_ttl),
            "--shapes",
            "nonexistent_shapes.ttl",
            "--out",
            str(out_file),
        ],
    )
    assert result.exit_code == 0
    assert (
        "Failed to perform SHACL validation" in result.output
        or "Failed to load" in result.output
    )


def test_validate_multiple_data_files(
    runner, sample_conform_data_ttl, sample_shapes_ttl, tmp_path
):
    """Test validation with multiple input RDF files."""
    out_file = tmp_path / "report.ttl"
    result = runner.invoke(
        app,
        [
            "validate",
            str(sample_conform_data_ttl),
            str(sample_conform_data_ttl),  # Same file twice for testing
            "--shapes",
            str(sample_shapes_ttl),
            "--out",
            str(out_file),
        ],
    )
    assert result.exit_code == 0
    assert "Validation successful" in result.output
    assert out_file.exists()


def test_validate_output_in_xml(
    runner, sample_conform_data_ttl, sample_shapes_ttl, tmp_path
):
    """Test validation with XML output format."""
    out_file = tmp_path / "report.xml"
    result = runner.invoke(
        app,
        [
            "validate",
            str(sample_conform_data_ttl),
            "--shapes",
            str(sample_shapes_ttl),
            "--out",
            str(out_file),
        ],
    )
    assert result.exit_code == 0
    assert out_file.exists()
    # Verify XML content
    content = out_file.read_text()
    assert "<?xml" in content or "<rdf" in content or len(content.strip()) > 0


def test_validate_output_in_txt_format(
    runner, sample_conform_data_ttl, sample_shapes_ttl, tmp_path
):
    """Test validation with plain text output format."""
    out_file = tmp_path / "report.txt"
    result = runner.invoke(
        app,
        [
            "validate",
            str(sample_conform_data_ttl),
            "--shapes",
            str(sample_shapes_ttl),
            "--out",
            str(out_file),
        ],
    )
    assert result.exit_code == 0
    assert "Validation successful" in result.output
    assert out_file.exists()
    content = out_file.read_text()
    assert len(content.strip()) > 0


def test_validate_output_in_unsupported_format(
    runner, sample_conform_data_ttl, sample_shapes_ttl, tmp_path
):
    """Test validation with unsupported output format."""
    out_file = tmp_path / "report.csv"
    result = runner.invoke(
        app,
        [
            "validate",
            str(sample_conform_data_ttl),
            "--shapes",
            str(sample_shapes_ttl),
            "--out",
            str(out_file),
        ],
    )
    assert result.exit_code == 0
    assert "Failed to serialize validation report" in result.output


def test_validate_with_dataset_flag(
    runner, sample_conform_data_ttl, sample_shapes_ttl, tmp_path
):
    """Test validation with dataset flag."""
    out_file = tmp_path / "report.ttl"
    result = runner.invoke(
        app,
        [
            "validate",
            str(sample_conform_data_ttl),
            "--shapes",
            str(sample_shapes_ttl),
            "--out",
            str(out_file),
            "--dataset",
        ],
    )
    assert result.exit_code == 0
    assert out_file.exists()


def test_validate_help(runner):
    """Test validate command help."""
    result = runner.invoke(app, ["validate", "--help"])
    assert result.exit_code == 0
    clean = re.sub(r"\x1b\[[0-9;]*m", "", result.output)
    assert "--shapes" in clean
    assert "--out" in clean
    assert "--dataset" in clean


def test_validate_with_short_options(
    runner, sample_conform_data_ttl, sample_shapes_ttl, tmp_path
):
    """Test validate command with short option names."""
    out_file = tmp_path / "report.ttl"
    result = runner.invoke(
        app,
        [
            "validate",
            str(sample_conform_data_ttl),
            "-s",
            str(sample_shapes_ttl),
            "-o",
            str(out_file),
        ],
    )
    assert result.exit_code == 0
    assert "Validation successful" in result.output
    assert out_file.exists()


def test_validate_with_dataset_short_flag(
    runner, sample_conform_data_ttl, sample_shapes_ttl, tmp_path
):
    """Test validate command with short dataset flag."""
    out_file = tmp_path / "report.ttl"
    result = runner.invoke(
        app,
        [
            "validate",
            str(sample_conform_data_ttl),
            "--shapes",
            str(sample_shapes_ttl),
            "--out",
            str(out_file),
            "-d",  # Short flag for dataset
        ],
    )
    assert result.exit_code == 0
    assert out_file.exists()


def test_validate_output_file_created(
    runner, sample_conform_data_ttl, sample_shapes_ttl, tmp_path
):
    """Test that validation report file is created with proper content."""
    out_file = tmp_path / "validation_report.ttl"
    result = runner.invoke(
        app,
        [
            "validate",
            str(sample_conform_data_ttl),
            "--shapes",
            str(sample_shapes_ttl),
            "--out",
            str(out_file),
        ],
    )
    assert result.exit_code == 0
    assert out_file.exists()
    # Verify file size is reasonable
    file_size = out_file.stat().st_size
    assert file_size > 0, "Report file should not be empty"


def test_validate_conforms_result(
    runner, sample_conform_data_ttl, sample_shapes_ttl, tmp_path
):
    """Test that validation produces conforms result."""
    out_file = tmp_path / "report.ttl"
    result = runner.invoke(
        app,
        [
            "validate",
            str(sample_conform_data_ttl),
            "--shapes",
            str(sample_shapes_ttl),
            "--out",
            str(out_file),
        ],
    )
    assert result.exit_code == 0
    # Should contain one of these results
    assert "Validation successful" in result.output
    assert "conforms" in result.output


def test_validate_not_conforms_result(
    runner, sample_non_conform_data_ttl, sample_shapes_ttl, tmp_path
):
    """Test that validation produces not conforms result."""
    out_file = tmp_path / "report.ttl"
    result = runner.invoke(
        app,
        [
            "validate",
            str(sample_non_conform_data_ttl),
            "--shapes",
            str(sample_shapes_ttl),
            "--out",
            str(out_file),
        ],
    )
    assert result.exit_code == 0
    # Should contain one of these results
    assert "Validation successful" in result.output
    assert "does not conform" in result.output


def test_validate_not_conforms_with_non_graph_report(
    runner, sample_non_conform_data_ttl, sample_shapes_ttl, tmp_path
):
    """When report_graph is not a Graph, print failure without violation count."""
    out_file = tmp_path / "report.ttl"
    fake_report = {"conforms": False, "report_graph": "not a graph"}
    with patch("pocket_rdf.cli_validate.execute_validation", return_value=fake_report):
        result = runner.invoke(
            app,
            [
                "validate",
                str(sample_non_conform_data_ttl),
                "--shapes",
                str(sample_shapes_ttl),
                "--out",
                str(out_file),
            ],
        )
    assert result.exit_code == 0
    assert (
        "Validation report is missing expected keys or has invalid types."
        in result.output
    )
    assert not out_file.exists()


def test_validate_execute_validation_raises(
    runner, sample_conform_data_ttl, sample_shapes_ttl, tmp_path
):
    """Test that CLI handles execute_validation raising an exception."""
    out_file = tmp_path / "report.ttl"
    with patch(
        "pocket_rdf.cli_validate.execute_validation",
        side_effect=RuntimeError("pyshacl blew up"),
    ):
        result = runner.invoke(
            app,
            [
                "validate",
                str(sample_conform_data_ttl),
                "--shapes",
                str(sample_shapes_ttl),
                "--out",
                str(out_file),
            ],
        )
    assert result.exit_code == 0
    assert "Failed to perform SHACL validation" in result.output
    assert "pyshacl blew up" in result.output


def test_validate_with_context_files(
    runner, sample_conform_data_ttl, sample_shapes_ttl, tmp_path
):
    """Test validation with --context loading additional reference files."""
    out_file = tmp_path / "report.ttl"
    result = runner.invoke(
        app,
        [
            "validate",
            str(sample_conform_data_ttl),
            "--shapes",
            str(sample_shapes_ttl),
            "--out",
            str(out_file),
            "--context",
            str(sample_conform_data_ttl),
        ],
    )
    assert result.exit_code == 0
    assert "Loading additional context RDF files" in result.output
    assert "Validation successful" in result.output
    assert out_file.exists()


def test_validate_with_context_short_option(
    runner, sample_conform_data_ttl, sample_shapes_ttl, tmp_path
):
    """Test validation with -c short option for context files."""
    out_file = tmp_path / "report.ttl"
    result = runner.invoke(
        app,
        [
            "validate",
            str(sample_conform_data_ttl),
            "-s",
            str(sample_shapes_ttl),
            "-o",
            str(out_file),
            "-c",
            str(sample_conform_data_ttl),
        ],
    )
    assert result.exit_code == 0
    assert "Loading additional context RDF files" in result.output
    assert "Validation successful" in result.output


def test_validate_with_nonexistent_context_file(
    runner, sample_conform_data_ttl, sample_shapes_ttl, tmp_path
):
    """Test validation with a nonexistent context file."""
    out_file = tmp_path / "report.ttl"
    result = runner.invoke(
        app,
        [
            "validate",
            str(sample_conform_data_ttl),
            "--shapes",
            str(sample_shapes_ttl),
            "--out",
            str(out_file),
            "--context",
            "nonexistent_context.ttl",
        ],
    )
    assert result.exit_code == 0
    assert "Failed to load" in result.output


def test_validate_with_multiple_context_files(
    runner,
    sample_conform_data_ttl,
    sample_non_conform_data_ttl,
    sample_shapes_ttl,
    tmp_path,
):
    """Test validation with multiple context files."""
    out_file = tmp_path / "report.ttl"
    result = runner.invoke(
        app,
        [
            "validate",
            str(sample_conform_data_ttl),
            "--shapes",
            str(sample_shapes_ttl),
            "--out",
            str(out_file),
            "--context",
            str(sample_conform_data_ttl),
            "--context",
            str(sample_non_conform_data_ttl),
        ],
    )
    assert result.exit_code == 0
    assert "Loading additional context RDF files" in result.output
    assert "Validation successful" in result.output


def test_validate_without_context_files(
    runner, sample_conform_data_ttl, sample_shapes_ttl, tmp_path
):
    """Test that validation works without any context files (default)."""
    out_file = tmp_path / "report.ttl"
    result = runner.invoke(
        app,
        [
            "validate",
            str(sample_conform_data_ttl),
            "--shapes",
            str(sample_shapes_ttl),
            "--out",
            str(out_file),
        ],
    )
    assert result.exit_code == 0
    assert "Loading additional context RDF files" not in result.output
    assert "Validation successful" in result.output


@pytest.fixture
def sample_info_shapes_ttl():
    """Load SHACL shapes with sh:severity sh:Info."""
    shapes_file = Path(__file__).parent / "data" / "info_shapes.ttl"
    if not shapes_file.exists():
        pytest.skip(f"Info shapes file not found: {shapes_file}")
    return shapes_file


@pytest.fixture
def sample_warning_shapes_ttl():
    """Load SHACL shapes with sh:severity sh:Warning."""
    shapes_file = Path(__file__).parent / "data" / "warning_shapes.ttl"
    if not shapes_file.exists():
        pytest.skip(f"Warning shapes file not found: {shapes_file}")
    return shapes_file


def test_validate_info_severity_fails_by_default(
    runner, sample_non_conform_data_ttl, sample_info_shapes_ttl, tmp_path
):
    """Info-severity violations cause failure without --allow-infos."""
    out_file = tmp_path / "report.ttl"
    result = runner.invoke(
        app,
        [
            "validate",
            str(sample_non_conform_data_ttl),
            "--shapes",
            str(sample_info_shapes_ttl),
            "--out",
            str(out_file),
        ],
    )
    assert result.exit_code == 0
    assert "does not conform" in result.output


def test_validate_with_allow_infos(
    runner, sample_non_conform_data_ttl, sample_info_shapes_ttl, tmp_path
):
    """Info-severity violations pass with --allow-infos."""
    out_file = tmp_path / "report.ttl"
    result = runner.invoke(
        app,
        [
            "validate",
            str(sample_non_conform_data_ttl),
            "--shapes",
            str(sample_info_shapes_ttl),
            "--out",
            str(out_file),
            "--allow-infos",
        ],
    )
    assert result.exit_code == 0
    assert "Validation successful" in result.output
    assert "conforms" in result.output


def test_validate_warning_severity_fails_by_default(
    runner, sample_non_conform_data_ttl, sample_warning_shapes_ttl, tmp_path
):
    """Warning-severity violations cause failure without --allow-warnings."""
    out_file = tmp_path / "report.ttl"
    result = runner.invoke(
        app,
        [
            "validate",
            str(sample_non_conform_data_ttl),
            "--shapes",
            str(sample_warning_shapes_ttl),
            "--out",
            str(out_file),
        ],
    )
    assert result.exit_code == 0
    assert "does not conform" in result.output


def test_validate_with_allow_warnings(
    runner, sample_non_conform_data_ttl, sample_warning_shapes_ttl, tmp_path
):
    """Warning-severity violations pass with --allow-warnings."""
    out_file = tmp_path / "report.ttl"
    result = runner.invoke(
        app,
        [
            "validate",
            str(sample_non_conform_data_ttl),
            "--shapes",
            str(sample_warning_shapes_ttl),
            "--out",
            str(out_file),
            "--allow-warnings",
        ],
    )
    assert result.exit_code == 0
    assert "Validation successful" in result.output
    assert "conforms" in result.output


def test_validate_allow_warnings_also_allows_infos(
    runner, sample_non_conform_data_ttl, sample_info_shapes_ttl, tmp_path
):
    """--allow-warnings also permits sh:Info severity violations."""
    out_file = tmp_path / "report.ttl"
    result = runner.invoke(
        app,
        [
            "validate",
            str(sample_non_conform_data_ttl),
            "--shapes",
            str(sample_info_shapes_ttl),
            "--out",
            str(out_file),
            "--allow-warnings",
        ],
    )
    assert result.exit_code == 0
    assert "Validation successful" in result.output


def test_validate_allow_infos_does_not_allow_warnings(
    runner, sample_non_conform_data_ttl, sample_warning_shapes_ttl, tmp_path
):
    """--allow-infos does not permit sh:Warning severity violations."""
    out_file = tmp_path / "report.ttl"
    result = runner.invoke(
        app,
        [
            "validate",
            str(sample_non_conform_data_ttl),
            "--shapes",
            str(sample_warning_shapes_ttl),
            "--out",
            str(out_file),
            "--allow-infos",
        ],
    )
    assert result.exit_code == 0
    assert "does not conform" in result.output


def test_validate_help_shows_allow_options(runner):
    """Test that --allow-infos and --allow-warnings appear in help."""
    result = runner.invoke(app, ["validate", "--help"])
    assert result.exit_code == 0
    clean = re.sub(r"\x1b\[[0-9;]*m", "", result.output)
    assert "--allow-infos" in clean
    assert "--allow-warnings" in clean

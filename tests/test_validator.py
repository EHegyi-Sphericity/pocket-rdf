import warnings
from pathlib import Path
from unittest.mock import patch

import pytest
from rdflib import Dataset, Graph, Literal, URIRef

from pocket_rdf.validator import (
    detect_output_format,
    execute_validation,
    get_nodes,
    serialize_report,
)


@pytest.fixture
def sample_graph():
    g = Graph()
    g.add(
        (
            URIRef("http://example.org/subject"),
            URIRef("http://example.org/predicate"),
            Literal("object"),
        )
    )
    g.add(
        (
            URIRef("http://example.org/subject"),
            URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
            URIRef("http://example.org/Class"),
        )
    )
    return g


@pytest.fixture
def sample_graph_nonconforming():
    g = Graph()
    g.add(
        (
            URIRef("http://example.org/subject"),
            URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
            URIRef("http://example.org/Class"),
        )
    )
    return g


@pytest.fixture
def sample_dataset():
    ds = Dataset()
    g1 = ds.graph(URIRef("http://example.org/graph1"))
    g1.add(
        (
            URIRef("http://example.org/subject"),
            URIRef("http://example.org/predicate"),
            Literal("object"),
        )
    )
    return ds


@pytest.fixture
def sample_shapes_file(tmp_path):
    shapes = tmp_path / "shapes.ttl"
    shapes.write_text("""@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix ex: <http://example.org/> .

ex:Shape a sh:NodeShape ;
    sh:targetClass ex:Class ;
    sh:property [
        sh:path ex:predicate ;
        sh:minCount 1 ;
    ] .
""")
    return shapes


@pytest.fixture
def sample_bad_shapes_file(tmp_path):
    bad_shapes = tmp_path / "bad_shapes.ttl"
    bad_shapes.write_text("""@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix ex: <http://example.org/> .

ex:Shape a sh:NodeShape ;
    sh:targetClass ex:Class ;
    sh:property not-a-valid-property-shape .
""")
    return bad_shapes


class TestDetectOutputFormat:
    def test_detect_format_ttl(self):
        assert detect_output_format(Path("out.ttl")) == "turtle"

    def test_detect_format_nt(self):
        assert detect_output_format(Path("out.nt")) == "nt"

    def test_detect_format_xml(self):
        assert detect_output_format(Path("out.xml")) == "xml"

    def test_detect_format_rdf(self):
        assert detect_output_format(Path("out.rdf")) == "xml"

    def test_detect_format_jsonld(self):
        assert detect_output_format(Path("out.jsonld")) == "json-ld"

    def test_detect_format_json(self):
        assert detect_output_format(Path("out.json")) == "json-ld"

    def test_detect_format_trig(self):
        assert detect_output_format(Path("out.trig")) == "trig"

    def test_detect_format_txt(self):
        assert detect_output_format(Path("out.txt")) == "txt"

    def test_detect_format_unsupported(self):
        assert detect_output_format(Path("out.nq")) is None
        assert detect_output_format(Path("out.csv")) is None
        assert detect_output_format(Path("out.unknown")) is None


class TestExecuteValidation:
    def test_execute_validation_conforms_graph(self, sample_graph, sample_shapes_file):
        result = execute_validation(sample_graph, sample_shapes_file)
        assert isinstance(result, dict)
        assert result["conforms"] is True
        assert "report_graph" in result

    def test_execute_validation_not_conform_graph(
        self, sample_graph_nonconforming, sample_shapes_file
    ):
        result = execute_validation(sample_graph_nonconforming, sample_shapes_file)
        assert isinstance(result, dict)
        assert result["conforms"] is False
        assert "report_graph" in result

    def test_execute_validation_conforms_dataset(
        self, sample_dataset, sample_shapes_file
    ):
        result = execute_validation(sample_dataset, sample_shapes_file)
        assert isinstance(result, dict)
        assert "conforms" in result
        assert "report_graph" in result

    def test_execute_validation_raises_runtime_error(
        self, sample_graph, sample_shapes_file
    ):
        with patch(
            "pocket_rdf.validator.validate",
            side_effect=Exception("pyshacl internal error"),
        ):
            with pytest.raises(RuntimeError, match="Failed to execute validation"):
                execute_validation(sample_graph, sample_shapes_file)

    def test_execute_validation_raises_on_non_graph_report(
        self, sample_graph, sample_shapes_file
    ):
        with patch(
            "pocket_rdf.validator.validate",
            return_value=(True, "not-a-graph", "text"),
        ):
            with pytest.raises(RuntimeError, match="not a valid RDF graph"):
                execute_validation(sample_graph, sample_shapes_file)

    def test_execute_validation_raises_on_non_string_report_text(
        self, sample_graph, sample_shapes_file
    ):
        with patch(
            "pocket_rdf.validator.validate",
            return_value=(True, Graph(), 12345),
        ):
            with pytest.raises(RuntimeError, match="not a valid string"):
                execute_validation(sample_graph, sample_shapes_file)


class TestSerializeReport:
    def test_serialize_report_ttl(self, tmp_path, sample_graph, sample_shapes_file):
        result = execute_validation(sample_graph, sample_shapes_file)
        outfile = tmp_path / "report.ttl"
        assert isinstance(result["report_graph"], Graph)
        assert isinstance(result["report_text"], str)
        serialize_report(result["report_graph"], result["report_text"], outfile)
        assert outfile.exists()
        content = outfile.read_text()
        assert "@prefix" in content or "<http://example.org/" in content

    def test_serialize_report_nt(self, tmp_path, sample_graph, sample_shapes_file):
        result = execute_validation(sample_graph, sample_shapes_file)
        outfile = tmp_path / "report.nt"
        assert isinstance(result["report_graph"], Graph)
        assert isinstance(result["report_text"], str)
        serialize_report(result["report_graph"], result["report_text"], outfile)
        assert outfile.exists()
        content = outfile.read_text()
        assert "<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>" in content

    def test_serialize_report_xml(self, tmp_path, sample_graph, sample_shapes_file):
        result = execute_validation(sample_graph, sample_shapes_file)
        outfile = tmp_path / "report.xml"
        assert isinstance(result["report_graph"], Graph)
        assert isinstance(result["report_text"], str)
        serialize_report(result["report_graph"], result["report_text"], outfile)
        assert outfile.exists()
        content = outfile.read_text()
        assert "<rdf:RDF" in content or "<rdf:Description" in content

    def test_serialize_report_jsonld(self, tmp_path, sample_graph, sample_shapes_file):
        result = execute_validation(sample_graph, sample_shapes_file)
        outfile = tmp_path / "test" / "report.jsonld"
        assert isinstance(result["report_graph"], Graph)
        assert isinstance(result["report_text"], str)
        serialize_report(result["report_graph"], result["report_text"], outfile)
        assert outfile.exists()
        content = outfile.read_text()
        assert "@type" in content or "@value" in content

    def test_serialize_report_json(self, tmp_path, sample_graph, sample_shapes_file):
        result = execute_validation(sample_graph, sample_shapes_file)
        outfile = tmp_path / "report.json"
        assert isinstance(result["report_graph"], Graph)
        assert isinstance(result["report_text"], str)
        serialize_report(result["report_graph"], result["report_text"], outfile)
        assert outfile.exists()
        content = outfile.read_text()
        print(content)
        assert "@type" in content or "@value" in content

    def test_serialize_report_txt(self, tmp_path, sample_graph, sample_shapes_file):
        result = execute_validation(sample_graph, sample_shapes_file)
        outfile = tmp_path / "report.txt"
        assert isinstance(result["report_graph"], Graph)
        assert isinstance(result["report_text"], str)
        serialize_report(result["report_graph"], result["report_text"], outfile)
        assert outfile.exists()
        content = outfile.read_text()
        assert "Conforms" in content or "Violation" in content or len(content) > 0

    def test_serialize_report_unsupported_format(
        self, tmp_path, sample_graph, sample_shapes_file
    ):
        result = execute_validation(sample_graph, sample_shapes_file)
        outfile = tmp_path / "report.csv"
        assert isinstance(result["report_graph"], Graph)
        assert isinstance(result["report_text"], str)
        with pytest.raises(ValueError, match="Unsupported serialization format"):
            serialize_report(result["report_graph"], result["report_text"], outfile)


class TestGetNodes:
    def test_get_nodes_from_graph(self, sample_graph):
        nodes = get_nodes(sample_graph)
        assert len(nodes) > 0
        assert "http://example.org/subject" in nodes

    def test_get_nodes_from_dataset(self, sample_dataset):
        nodes = get_nodes(sample_dataset)
        assert len(nodes) > 0
        assert "http://example.org/subject" in nodes

    def test_get_nodes_empty_graph(self):
        g = Graph()
        nodes = get_nodes(g)
        assert nodes == []

    def test_get_nodes_empty_dataset(self):
        ds = Dataset()
        nodes = get_nodes(ds)
        assert nodes == []


class TestExecuteValidationWithContext:
    def test_validation_with_context_graph(self, sample_graph, sample_shapes_file):
        context = Graph()
        context.add(
            (
                URIRef("http://example.org/other"),
                URIRef("http://example.org/predicate"),
                Literal("value"),
            )
        )
        result = execute_validation(
            sample_graph, sample_shapes_file, context_graph=context
        )
        assert isinstance(result, dict)
        assert "conforms" in result
        assert "report_graph" in result

    def test_validation_with_none_context(self, sample_graph, sample_shapes_file):
        result = execute_validation(
            sample_graph, sample_shapes_file, context_graph=None
        )
        assert result["conforms"] is True

    def test_validation_runtime_error(self, sample_graph, sample_bad_shapes_file):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ResourceWarning)
            with pytest.raises(RuntimeError, match="Failed to execute validation"):
                execute_validation(sample_graph, sample_bad_shapes_file)


class TestAllowInfosWarnings:
    @pytest.fixture
    def info_shapes_file(self, tmp_path):
        shapes = tmp_path / "info_shapes.ttl"
        shapes.write_text("""@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix ex: <http://example.org/> .

ex:InfoShape a sh:NodeShape ;
    sh:targetClass ex:Class ;
    sh:severity sh:Info ;
    sh:property [
        sh:path ex:optionalProp ;
        sh:minCount 1 ;
    ] .
""")
        return shapes

    @pytest.fixture
    def warning_shapes_file(self, tmp_path):
        shapes = tmp_path / "warning_shapes.ttl"
        shapes.write_text("""@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix ex: <http://example.org/> .

ex:WarningShape a sh:NodeShape ;
    sh:targetClass ex:Class ;
    sh:severity sh:Warning ;
    sh:property [
        sh:path ex:recommendedProp ;
        sh:minCount 1 ;
    ] .
""")
        return shapes

    @pytest.fixture
    def violating_graph(self):
        g = Graph()
        g.add(
            (
                URIRef("http://example.org/subject"),
                URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
                URIRef("http://example.org/Class"),
            )
        )
        return g

    def test_info_severity_fails_without_allow_infos(
        self, violating_graph, info_shapes_file
    ):
        result = execute_validation(violating_graph, info_shapes_file)
        assert result["conforms"] is False

    def test_info_severity_passes_with_allow_infos(
        self, violating_graph, info_shapes_file
    ):
        result = execute_validation(violating_graph, info_shapes_file, allow_infos=True)
        assert result["conforms"] is True

    def test_warning_severity_fails_without_allow_warnings(
        self, violating_graph, warning_shapes_file
    ):
        result = execute_validation(violating_graph, warning_shapes_file)
        assert result["conforms"] is False

    def test_warning_severity_passes_with_allow_warnings(
        self, violating_graph, warning_shapes_file
    ):
        result = execute_validation(
            violating_graph, warning_shapes_file, allow_warnings=True
        )
        assert result["conforms"] is True

    def test_allow_warnings_also_allows_infos(self, violating_graph, info_shapes_file):
        result = execute_validation(
            violating_graph, info_shapes_file, allow_warnings=True
        )
        assert result["conforms"] is True

    def test_allow_infos_does_not_allow_warnings(
        self, violating_graph, warning_shapes_file
    ):
        result = execute_validation(
            violating_graph, warning_shapes_file, allow_infos=True
        )
        assert result["conforms"] is False


class TestDetectOutputFormatCaseInsensitive:
    def test_detect_format_uppercase_ttl(self):
        assert detect_output_format(Path("out.TTL")) == "turtle"

    def test_detect_format_mixed_case_jsonld(self):
        assert detect_output_format(Path("out.JsonLD")) == "json-ld"

    def test_serialize_report_trig(self, tmp_path, sample_graph, sample_shapes_file):
        result = execute_validation(sample_graph, sample_shapes_file)
        outfile = tmp_path / "report.trig"
        assert isinstance(result["report_graph"], Graph)
        assert isinstance(result["report_text"], str)
        serialize_report(result["report_graph"], result["report_text"], outfile)
        assert outfile.exists()
        content = outfile.read_text()
        assert "@prefix" in content or "<http://example.org/" in content

    def test_serialize_report_unsupported(
        self, tmp_path, sample_graph, sample_shapes_file
    ):
        result = execute_validation(sample_graph, sample_shapes_file)
        outfile = tmp_path / "report.unknown"
        assert isinstance(result["report_graph"], Graph)
        assert isinstance(result["report_text"], str)
        with pytest.raises(ValueError, match="Unsupported serialization format"):
            serialize_report(result["report_graph"], result["report_text"], outfile)

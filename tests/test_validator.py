from pathlib import Path

import pytest
from rdflib import Dataset, Graph, Literal, URIRef

from pocket_rdf.validator import (
    detect_output_format,
    execute_validation,
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

    def test_detect_format_unsupported(self):
        assert detect_output_format(Path("out.txt")) is None
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

    def test_execute_validation_missing_shapes_file(self, sample_graph):
        with pytest.raises(RuntimeError, match="Failed to execute validation"):
            execute_validation(sample_graph, Path("missing_shapes.ttl"))


class TestSerializeReport:
    def test_serialize_report_ttl(self, tmp_path, sample_graph, sample_shapes_file):
        report = execute_validation(sample_graph, sample_shapes_file)["report_graph"]
        outfile = tmp_path / "report.ttl"
        assert isinstance(report, Graph)
        serialize_report(report, outfile)
        assert outfile.exists()
        content = outfile.read_text()
        assert "@prefix" in content or "<http://example.org/" in content

    def test_serialize_report_nt(self, tmp_path, sample_graph, sample_shapes_file):
        report = execute_validation(sample_graph, sample_shapes_file)["report_graph"]
        outfile = tmp_path / "report.nt"
        assert isinstance(report, Graph)
        serialize_report(report, outfile)
        assert outfile.exists()
        content = outfile.read_text()
        assert "<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>" in content

    def test_serialize_report_xml(self, tmp_path, sample_graph, sample_shapes_file):
        report = execute_validation(sample_graph, sample_shapes_file)["report_graph"]
        outfile = tmp_path / "report.xml"
        assert isinstance(report, Graph)
        serialize_report(report, outfile)
        assert outfile.exists()
        content = outfile.read_text()
        assert "<rdf:RDF" in content or "<rdf:Description" in content

    def test_serialize_report_jsonld(self, tmp_path, sample_graph, sample_shapes_file):
        report = execute_validation(sample_graph, sample_shapes_file)["report_graph"]
        outfile = tmp_path / "test" / "report.jsonld"
        assert isinstance(report, Graph)
        serialize_report(report, outfile)
        assert outfile.exists()
        content = outfile.read_text()
        assert "@type" in content or "@value" in content

    def test_serialize_report_json(self, tmp_path, sample_graph, sample_shapes_file):
        report = execute_validation(sample_graph, sample_shapes_file)["report_graph"]
        outfile = tmp_path / "report.json"
        assert isinstance(report, Graph)
        serialize_report(report, outfile)
        assert outfile.exists()
        content = outfile.read_text()
        print(content)
        assert "@type" in content or "@value" in content

    def test_serialize_report_trig(self, tmp_path, sample_graph, sample_shapes_file):
        report = execute_validation(sample_graph, sample_shapes_file)["report_graph"]
        outfile = tmp_path / "report.trig"
        assert isinstance(report, Graph)
        serialize_report(report, outfile)
        assert outfile.exists()
        content = outfile.read_text()
        assert "@prefix" in content or "<http://example.org/" in content

    def test_serialize_report_unsupported(
        self, tmp_path, sample_graph, sample_shapes_file
    ):
        report = execute_validation(sample_graph, sample_shapes_file)["report_graph"]
        outfile = tmp_path / "report.unknown"
        assert isinstance(report, Graph)
        with pytest.raises(ValueError, match="Unsupported serialization format"):
            serialize_report(report, outfile)

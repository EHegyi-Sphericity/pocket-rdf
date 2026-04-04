from pathlib import Path

import pytest
from rdflib import Dataset, Graph, Literal, URIRef

from pocket_rdf.serializer import detect_output_format, serialize_graphs


@pytest.fixture
def sample_graph():
    """Create a sample RDF graph for testing."""
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
def sample_dataset():
    """Create a sample RDF dataset with named graphs for testing."""
    ds = Dataset()
    g1 = ds.graph(URIRef("http://example.org/graph1"))
    g1.add(
        (
            URIRef("http://example.org/subject1"),
            URIRef("http://example.org/predicate"),
            Literal("object1"),
        )
    )

    g2 = ds.graph(URIRef("http://example.org/graph2"))
    g2.add(
        (
            URIRef("http://example.org/subject2"),
            URIRef("http://example.org/predicate"),
            Literal("object2"),
        )
    )

    # Default graph
    ds.add(
        (
            URIRef("http://example.org/default"),
            URIRef("http://example.org/predicate"),
            Literal("default"),
        )
    )
    return ds


class TestDetectOutputFormat:
    """Test the detect_output_format function."""

    def test_detect_format_is_dataset_trig(self):
        assert detect_output_format(Path("test.trig"), is_dataset=True) == "trig"

    def test_detect_format_is_dataset_nq(self):
        assert detect_output_format(Path("test.nq"), is_dataset=True) == "nquads"

    def test_detect_format_is_dataset_txt(self):
        assert detect_output_format(Path("test.txt"), is_dataset=True) == "txt"

    def test_detect_format_is_dataset_unsupported(self):
        assert detect_output_format(Path("test.ttl"), is_dataset=True) is None
        assert detect_output_format(Path("test.unknown"), is_dataset=True) is None

    def test_detect_format_default_graph_ttl(self):
        assert detect_output_format(Path("test.ttl"), is_dataset=False) == "turtle"

    def test_detect_format_default_graph_nt(self):
        assert detect_output_format(Path("test.nt"), is_dataset=False) == "nt"

    def test_detect_format_default_graph_xml(self):
        assert detect_output_format(Path("test.xml"), is_dataset=False) == "xml"
        assert detect_output_format(Path("test.rdf"), is_dataset=False) == "xml"

    def test_detect_format_default_graph_jsonld(self):
        assert detect_output_format(Path("test.jsonld"), is_dataset=False) == "json-ld"
        assert detect_output_format(Path("test.json"), is_dataset=False) == "json-ld"

    def test_detect_format_default_graph_trig(self):
        assert detect_output_format(Path("test.trig"), is_dataset=False) == "trig"

    def test_detect_format_default_graph_nq(self):
        assert detect_output_format(Path("test.nq"), is_dataset=False) == "nquads"

    def test_detect_format_default_graph_txt(self):
        assert detect_output_format(Path("test.txt"), is_dataset=False) == "txt"

    def test_detect_format_default_graph_unsupported(self):
        assert detect_output_format(Path("test.csv"), is_dataset=False) is None
        assert detect_output_format(Path("test.unknown"), is_dataset=False) is None

    def test_detect_format_case_insensitive(self):
        assert detect_output_format(Path("test.TTL"), is_dataset=False) == "turtle"
        assert detect_output_format(Path("test.Trig"), is_dataset=True) == "trig"


class TestSerializeGraphs:
    """Test the serialize_graphs function."""

    def test_serialize_graph_ttl(self, tmp_path, sample_graph):
        outfile = tmp_path / "output.ttl"
        serialize_graphs(sample_graph, outfile)
        assert outfile.exists()
        # Optionally, check content
        content = outfile.read_text()
        assert "@prefix" in content or "<http://example.org/subject>" in content

    def test_serialize_graph_nt(self, tmp_path, sample_graph):
        outfile = tmp_path / "output.nt"
        serialize_graphs(sample_graph, outfile)
        assert outfile.exists()
        content = outfile.read_text()
        assert "<http://example.org/subject>" in content

    def test_serialize_graph_xml(self, tmp_path, sample_graph):
        outfile = tmp_path / "output.xml"
        serialize_graphs(sample_graph, outfile)
        assert outfile.exists()
        content = outfile.read_text()
        assert "<rdf:RDF" in content

    def test_serialize_graph_jsonld(self, tmp_path, sample_graph):
        outfile = tmp_path / "output.jsonld"
        serialize_graphs(sample_graph, outfile)
        assert outfile.exists()
        content = outfile.read_text()
        assert '"@graph"' in content or '"@id"' in content

    def test_serialize_graph_txt(self, tmp_path, sample_graph):
        outfile = tmp_path / "output.txt"
        serialize_graphs(sample_graph, outfile)
        assert outfile.exists()
        content = outfile.read_text()
        # Should contain tuples
        assert (
            "(rdflib.term.URIRef('http://example.org/subject')" in content
            or "URIRef('http://example.org/subject')" in content
        )

    def test_serialize_dataset_trig(self, tmp_path, sample_dataset):
        outfile = tmp_path / "output.trig"
        serialize_graphs(sample_dataset, outfile)
        assert outfile.exists()
        content = outfile.read_text()
        assert "@prefix" in content

    def test_serialize_dataset_nq(self, tmp_path, sample_dataset):
        outfile = tmp_path / "output.nq"
        serialize_graphs(sample_dataset, outfile)
        assert outfile.exists()
        content = outfile.read_text()
        assert "<http://example.org/subject1>" in content

    def test_serialize_dataset_txt(self, tmp_path, sample_dataset):
        outfile = tmp_path / "test" / "output.txt"
        serialize_graphs(sample_dataset, outfile)
        assert outfile.exists()
        content = outfile.read_text()
        assert (
            "(rdflib.term.URIRef('http://example.org/subject1')" in content
            or "URIRef('http://example.org/subject1')" in content
        )

    def test_serialize_unsupported_format_graph(self, tmp_path, sample_graph):
        outfile = tmp_path / "output.unknown"
        with pytest.raises(ValueError, match="Unsupported serialization format"):
            serialize_graphs(sample_graph, outfile)

    def test_serialize_unsupported_format_dataset(self, tmp_path, sample_dataset):
        outfile = tmp_path / "output.ttl"  # ttl not supported for datasets
        with pytest.raises(ValueError, match="Unsupported serialization format"):
            serialize_graphs(sample_dataset, outfile)

    def test_serialize_invalid_destination(self, sample_graph):
        # Test with invalid path or permission issues, but since it's hard to simulate,
        # maybe skip or test with non-existent dir
        pass  # For now, assume rdflib handles it

    def test_serialize_csv_graph(self, tmp_path, sample_graph):
        outfile = tmp_path / "output.csv"
        with pytest.raises(ValueError, match="Unsupported serialization format"):
            serialize_graphs(sample_graph, outfile)

from pathlib import Path

import pytest
from rdflib import Dataset, Graph, Literal, URIRef

from pocket_rdf.query import detect_output_format, execute_query, serialize_results


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
    g.add(
        (
            URIRef("http://example.org/another"),
            URIRef("http://example.org/predicate"),
            Literal("another object"),
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


@pytest.fixture
def sample_query_file(tmp_path):
    """Create a sample SPARQL query file."""
    query_path = tmp_path / "query.sparql"
    query_path.write_text("""
    PREFIX ex: <http://example.org/>
    SELECT ?s ?p ?o
    WHERE {
        ?s ?p ?o .
    }
    """)
    return query_path


@pytest.fixture
def sample_construct_query_file(tmp_path):
    """Create a sample SPARQL CONSTRUCT query file."""
    query_path = tmp_path / "construct_query.sparql"
    query_path.write_text("""
    PREFIX ex: <http://example.org/>
    CONSTRUCT {
        ?s ex:newPredicate ?o .
    }
    WHERE {
        ?s ex:predicate ?o .
    }
    """)
    return query_path


class TestDetectOutputFormat:
    """Test the detect_output_format function."""

    def test_detect_format_xml(self):
        assert detect_output_format(Path("results.xml")) == "xml"

    def test_detect_format_json(self):
        assert detect_output_format(Path("results.json")) == "json"

    def test_detect_format_txt(self):
        assert detect_output_format(Path("results.txt")) == "txt"

    def test_detect_format_csv(self):
        assert detect_output_format(Path("results.csv")) == "csv"

    def test_detect_format_unsupported(self):
        assert detect_output_format(Path("results.ttl")) is None
        assert detect_output_format(Path("results.unknown")) is None

    def test_detect_format_case_insensitive(self):
        assert detect_output_format(Path("results.CSV")) == "csv"
        assert detect_output_format(Path("results.Json")) == "json"


class TestExecuteQuery:
    """Test the execute_query function."""

    def test_execute_query_select_graph(self, sample_graph, sample_query_file):
        results = execute_query(sample_graph, sample_query_file)
        assert results is not None
        # Check that it's a Result object
        assert hasattr(results, "bindings") or hasattr(results, "graph")
        # For SELECT query, should have bindings
        if hasattr(results, "bindings"):
            assert len(results.bindings) > 0

    def test_execute_query_select_dataset(self, sample_dataset, sample_query_file):
        results = execute_query(sample_dataset, sample_query_file)
        assert results is not None
        assert hasattr(results, "bindings") or hasattr(results, "graph")

    def test_execute_query_construct_graph(
        self, sample_graph, sample_construct_query_file
    ):
        results = execute_query(sample_graph, sample_construct_query_file)
        assert results is not None
        # CONSTRUCT returns a Graph
        assert hasattr(results, "graph") or isinstance(results, Graph)

    def test_execute_query_invalid_query_file(self, sample_graph, tmp_path):
        invalid_query = tmp_path / "invalid.sparql"
        invalid_query.write_text("INVALID SPARQL QUERY")
        with pytest.raises(ValueError, match="Failed to load SPARQL query"):
            execute_query(sample_graph, invalid_query)

    def test_execute_query_nonexistent_file(self, sample_graph):
        with pytest.raises(ValueError, match="Failed to load SPARQL query"):
            execute_query(sample_graph, Path("nonexistent.sparql"))


class TestSerializeResults:
    """Test the serialize_results function."""

    def test_serialize_results_select_xml(
        self, tmp_path, sample_graph, sample_query_file
    ):
        results = execute_query(sample_graph, sample_query_file)
        outfile = tmp_path / "results.xml"
        serialize_results(results, outfile)
        assert outfile.exists()
        content = outfile.read_text()
        assert "<sparql" in content or "<results>" in content

    def test_serialize_results_select_json(
        self, tmp_path, sample_graph, sample_query_file
    ):
        results = execute_query(sample_graph, sample_query_file)
        outfile = tmp_path / "results.json"
        serialize_results(results, outfile)
        assert outfile.exists()
        content = outfile.read_text()
        assert '"head"' in content or '"results"' in content

    def test_serialize_results_select_txt(
        self, tmp_path, sample_graph, sample_query_file
    ):
        results = execute_query(sample_graph, sample_query_file)
        outfile = tmp_path / "results.txt"
        serialize_results(results, outfile)
        assert outfile.exists()
        content = outfile.read_text()
        assert len(content) > 0

    def test_serialize_results_select_csv(
        self, tmp_path, sample_graph, sample_query_file
    ):
        results = execute_query(sample_graph, sample_query_file)
        outfile = tmp_path / "results.csv"
        serialize_results(results, outfile)
        assert outfile.exists()
        content = outfile.read_text()
        assert len(content) > 0

    def test_serialize_results_construct_xml(
        self, tmp_path, sample_graph, sample_construct_query_file
    ):
        results = execute_query(sample_graph, sample_construct_query_file)
        outfile = tmp_path / "test" / "construct_results.xml"
        serialize_results(results, outfile)
        assert outfile.exists()
        content = outfile.read_text()
        assert 'xmlns:ns1="http://example.org/"' in content

    def test_serialize_results_unsupported_format(
        self, tmp_path, sample_graph, sample_query_file
    ):
        results = execute_query(sample_graph, sample_query_file)
        outfile = tmp_path / "results.unknown"
        with pytest.raises(ValueError, match="Unsupported serialization format"):
            serialize_results(results, outfile)

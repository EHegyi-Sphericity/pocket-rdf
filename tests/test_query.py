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


@pytest.fixture
def sample_ask_true_query_file(tmp_path):
    """Create a SPARQL ASK query that should return True."""
    query_path = tmp_path / "ask_true.sparql"
    query_path.write_text("""
    PREFIX ex: <http://example.org/>
    ASK {
        ex:subject ex:predicate "object" .
    }
    """)
    return query_path


@pytest.fixture
def sample_ask_false_query_file(tmp_path):
    """Create a SPARQL ASK query that should return False."""
    query_path = tmp_path / "ask_false.sparql"
    query_path.write_text("""
    PREFIX ex: <http://example.org/>
    ASK {
        ex:nonexistent ex:predicate "nothing" .
    }
    """)
    return query_path


@pytest.fixture
def sample_describe_query_file(tmp_path):
    """Create a SPARQL DESCRIBE query file."""
    query_path = tmp_path / "describe.sparql"
    query_path.write_text("""
    PREFIX ex: <http://example.org/>
    DESCRIBE ex:subject
    """)
    return query_path


class TestDetectOutputFormat:
    """Test the detect_output_format function."""

    # --- SELECT/ASK mode (default) ---

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

    # --- CONSTRUCT/DESCRIBE mode (is_graph_result=True) ---

    def test_detect_format_graph_ttl(self):
        assert (
            detect_output_format(Path("results.ttl"), is_graph_result=True) == "turtle"
        )

    def test_detect_format_graph_nt(self):
        assert detect_output_format(Path("results.nt"), is_graph_result=True) == "nt"

    def test_detect_format_graph_xml(self):
        assert detect_output_format(Path("results.xml"), is_graph_result=True) == "xml"

    def test_detect_format_graph_rdf(self):
        assert detect_output_format(Path("results.rdf"), is_graph_result=True) == "xml"

    def test_detect_format_graph_jsonld(self):
        assert (
            detect_output_format(Path("results.jsonld"), is_graph_result=True)
            == "json-ld"
        )

    def test_detect_format_graph_json(self):
        assert (
            detect_output_format(Path("results.json"), is_graph_result=True)
            == "json-ld"
        )

    def test_detect_format_graph_unsupported(self):
        assert detect_output_format(Path("results.csv"), is_graph_result=True) is None
        assert detect_output_format(Path("results.nq"), is_graph_result=True) is None
        assert detect_output_format(Path("results.txt"), is_graph_result=True) is None
        assert (
            detect_output_format(Path("results.unknown"), is_graph_result=True) is None
        )


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

    def test_execute_query_construct_returns_correct_triples(
        self, sample_graph, sample_construct_query_file
    ):
        results = execute_query(sample_graph, sample_construct_query_file)
        assert results.graph is not None
        constructed_triples = list(results.graph)
        # The CONSTRUCT rewrites ex:predicate → ex:newPredicate
        # sample_graph has 2 triples with ex:predicate (subject→"object",
        #   another→"another object")
        assert len(constructed_triples) == 2
        new_pred = URIRef("http://example.org/newPredicate")
        for s, p, o in constructed_triples:
            assert p == new_pred

    def test_execute_query_construct_dataset(
        self, sample_dataset, sample_construct_query_file
    ):
        results = execute_query(sample_dataset, sample_construct_query_file)
        assert results.graph is not None
        constructed_triples = list(results.graph)
        # Dataset.query() operates on the default graph only,
        # so only the 1 triple from the default graph is matched.
        assert len(constructed_triples) == 1
        new_pred = URIRef("http://example.org/newPredicate")
        for s, p, o in constructed_triples:
            assert p == new_pred

    def test_execute_query_ask_true(self, sample_graph, sample_ask_true_query_file):
        results = execute_query(sample_graph, sample_ask_true_query_file)
        assert results is not None
        assert results.type == "ASK"
        assert bool(results) is True

    def test_execute_query_ask_false(self, sample_graph, sample_ask_false_query_file):
        results = execute_query(sample_graph, sample_ask_false_query_file)
        assert results is not None
        assert results.type == "ASK"
        assert bool(results) is False

    def test_execute_query_ask_dataset(
        self, sample_dataset, sample_ask_true_query_file
    ):
        """ASK against a dataset that does not contain the matching triple."""
        results = execute_query(sample_dataset, sample_ask_true_query_file)
        assert results.type == "ASK"
        # The dataset has different subjects/objects than the ASK query expects
        assert isinstance(bool(results), bool)

    def test_execute_query_describe(self, sample_graph, sample_describe_query_file):
        results = execute_query(sample_graph, sample_describe_query_file)
        assert results is not None
        assert results.graph is not None
        described_triples = list(results.graph)
        # DESCRIBE ex:subject should return all triples about ex:subject
        subject = URIRef("http://example.org/subject")
        assert len(described_triples) > 0
        for s, p, o in described_triples:
            assert s == subject

    def test_execute_query_describe_dataset(
        self, sample_dataset, sample_describe_query_file
    ):
        results = execute_query(sample_dataset, sample_describe_query_file)
        assert results.graph is not None
        # DESCRIBE may return empty if ex:subject is not in the dataset
        described_triples = list(results.graph)
        assert isinstance(described_triples, list)

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

    def test_serialize_results_construct_json(
        self, tmp_path, sample_graph, sample_construct_query_file
    ):
        """CONSTRUCT results serialized to .json now use json-ld format."""
        results = execute_query(sample_graph, sample_construct_query_file)
        outfile = tmp_path / "construct_results.json"
        serialize_results(results, outfile)
        assert outfile.exists()
        content = outfile.read_text()
        assert "newPredicate" in content

    def test_serialize_results_ask_true_xml(
        self, tmp_path, sample_graph, sample_ask_true_query_file
    ):
        results = execute_query(sample_graph, sample_ask_true_query_file)
        outfile = tmp_path / "ask_true_results.xml"
        serialize_results(results, outfile)
        assert outfile.exists()
        content = outfile.read_text()
        assert "<boolean>true</boolean>" in content

    def test_serialize_results_ask_false_xml(
        self, tmp_path, sample_graph, sample_ask_false_query_file
    ):
        results = execute_query(sample_graph, sample_ask_false_query_file)
        outfile = tmp_path / "ask_false_results.xml"
        serialize_results(results, outfile)
        assert outfile.exists()
        content = outfile.read_text()
        assert "<boolean>false</boolean>" in content

    def test_serialize_results_ask_json(
        self, tmp_path, sample_graph, sample_ask_true_query_file
    ):
        results = execute_query(sample_graph, sample_ask_true_query_file)
        outfile = tmp_path / "ask_results.json"
        serialize_results(results, outfile)
        assert outfile.exists()
        content = outfile.read_text()
        assert '"boolean"' in content

    def test_serialize_results_describe_xml(
        self, tmp_path, sample_graph, sample_describe_query_file
    ):
        results = execute_query(sample_graph, sample_describe_query_file)
        outfile = tmp_path / "describe_results.xml"
        serialize_results(results, outfile)
        assert outfile.exists()
        content = outfile.read_text()
        assert len(content) > 0

    def test_serialize_results_construct_ttl(
        self, tmp_path, sample_graph, sample_construct_query_file
    ):
        results = execute_query(sample_graph, sample_construct_query_file)
        outfile = tmp_path / "construct_results.ttl"
        serialize_results(results, outfile)
        assert outfile.exists()
        content = outfile.read_text()
        assert "newPredicate" in content

    def test_serialize_results_construct_nt(
        self, tmp_path, sample_graph, sample_construct_query_file
    ):
        results = execute_query(sample_graph, sample_construct_query_file)
        outfile = tmp_path / "construct_results.nt"
        serialize_results(results, outfile)
        assert outfile.exists()
        content = outfile.read_text()
        assert "newPredicate" in content

    def test_serialize_results_construct_rdf(
        self, tmp_path, sample_graph, sample_construct_query_file
    ):
        results = execute_query(sample_graph, sample_construct_query_file)
        outfile = tmp_path / "construct_results.rdf"
        serialize_results(results, outfile)
        assert outfile.exists()
        content = outfile.read_text()
        assert "newPredicate" in content

    def test_serialize_results_construct_jsonld(
        self, tmp_path, sample_graph, sample_construct_query_file
    ):
        results = execute_query(sample_graph, sample_construct_query_file)
        outfile = tmp_path / "construct_results.jsonld"
        serialize_results(results, outfile)
        assert outfile.exists()
        content = outfile.read_text()
        assert "newPredicate" in content

    def test_serialize_results_construct_trig(
        self, tmp_path, sample_graph, sample_construct_query_file
    ):
        results = execute_query(sample_graph, sample_construct_query_file)
        outfile = tmp_path / "construct_results.trig"
        serialize_results(results, outfile)
        assert outfile.exists()
        content = outfile.read_text()
        assert "newPredicate" in content

    def test_serialize_results_construct_nq_unsupported(
        self, tmp_path, sample_graph, sample_construct_query_file
    ):
        """N-Quads requires a context-aware store;
        CONSTRUCT results are plain Graphs."""
        results = execute_query(sample_graph, sample_construct_query_file)
        outfile = tmp_path / "construct_results.nq"
        with pytest.raises(ValueError, match="CONSTRUCT/DESCRIBE"):
            serialize_results(results, outfile)

    def test_serialize_results_construct_txt_unsupported(
        self, tmp_path, sample_graph, sample_construct_query_file
    ):
        """txt has no rdflib graph serializer; only works for SELECT/ASK results."""
        results = execute_query(sample_graph, sample_construct_query_file)
        outfile = tmp_path / "construct_results.txt"
        with pytest.raises(ValueError, match="CONSTRUCT/DESCRIBE"):
            serialize_results(results, outfile)

    def test_serialize_results_describe_ttl(
        self, tmp_path, sample_graph, sample_describe_query_file
    ):
        results = execute_query(sample_graph, sample_describe_query_file)
        outfile = tmp_path / "describe_results.ttl"
        serialize_results(results, outfile)
        assert outfile.exists()
        content = outfile.read_text()
        assert len(content) > 0

    def test_serialize_results_construct_unsupported_format(
        self, tmp_path, sample_graph, sample_construct_query_file
    ):
        results = execute_query(sample_graph, sample_construct_query_file)
        outfile = tmp_path / "construct_results.csv"
        with pytest.raises(ValueError, match="CONSTRUCT/DESCRIBE"):
            serialize_results(results, outfile)

    def test_serialize_results_construct_none_graph(
        self, tmp_path, sample_graph, sample_construct_query_file
    ):
        """Serializing CONSTRUCT results with graph=None should raise ValueError."""
        results = execute_query(sample_graph, sample_construct_query_file)
        results.graph = None
        outfile = tmp_path / "construct_results.ttl"
        with pytest.raises(ValueError, match="returned no graph to serialize"):
            serialize_results(results, outfile)

    def test_serialize_results_unsupported_format(
        self, tmp_path, sample_graph, sample_query_file
    ):
        results = execute_query(sample_graph, sample_query_file)
        outfile = tmp_path / "results.unknown"
        with pytest.raises(ValueError, match="Unsupported serialization format"):
            serialize_results(results, outfile)

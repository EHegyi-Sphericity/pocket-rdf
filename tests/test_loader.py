from pathlib import Path

import pytest
from rdflib import Dataset

from pocket_rdf.loader import assert_supported_format, detect_format, load_graphs


@pytest.fixture
def sample_data_ttl(tmp_path):
    file_path = tmp_path / "data.ttl"
    file_path.write_text("""@prefix ex: <http://example.org/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

ex:subject rdf:type ex:Class ;
    ex:predicate "object" .""")
    return file_path


@pytest.fixture
def sample_data_xml(tmp_path):
    file_path = tmp_path / "data.rdf"
    file_path.write_text("""<?xml version='1.0'?>
<rdf:RDF xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#'
                         xmlns:ex='http://example.org/'>
  <rdf:Description rdf:about='http://example.org/subject'>
    <rdf:type rdf:resource='http://example.org/Class'/>
    <ex:predicate>object</ex:predicate>
  </rdf:Description>
</rdf:RDF>""")
    return file_path


def test_detect_format_known_extensions():
    assert detect_format(Path("foo.ttl")) == "turtle"
    assert detect_format(Path("foo.nt")) == "nt"
    assert detect_format(Path("foo.xml")) == "xml"
    assert detect_format(Path("foo.rdf")) == "xml"
    assert detect_format(Path("foo.jsonld")) == "json-ld"


def test_detect_format_unknown_extension():
    assert detect_format(Path("foo.unknown")) is None


def test_assert_supported_format_file_missing(tmp_path):
    with pytest.raises(ValueError, match="File not found"):
        assert_supported_format(tmp_path / "nonexistent.ttl")


def test_assert_supported_format_unsupported_extension(tmp_path):
    bad_file = tmp_path / "bad.txt"
    bad_file.write_text("dummy")
    with pytest.raises(ValueError, match="Unsupported RDF format"):
        assert_supported_format(bad_file)


def test_load_graphs_single_graph(sample_data_ttl, sample_data_xml):
    graph, fails = load_graphs([sample_data_ttl, sample_data_xml], use_dataset=False)
    assert len(fails) == 0
    assert graph is not None
    # verify data loaded
    assert len(graph) >= 2


def test_load_graphs_named_graphs(sample_data_ttl, sample_data_xml):
    ds, fails = load_graphs([sample_data_ttl, sample_data_xml], use_dataset=True)
    assert len(fails) == 0
    assert isinstance(ds, Dataset)
    # ensure dataset has named graphs for each input file plus the default graph
    graphs = list(ds.graphs())
    assert len(graphs) == 3
    graph_ids = {str(g.identifier) for g in graphs if g != ds.default_graph}
    assert sample_data_ttl.resolve().as_uri() in graph_ids
    assert sample_data_xml.resolve().as_uri() in graph_ids
    assert ds.default_graph is not None


def test_load_graphs_with_invalid_file(sample_data_ttl, tmp_path):
    bad_file = tmp_path / "bad.ttl"
    bad_file.write_text("not rdf")
    graph, fails = load_graphs([sample_data_ttl, bad_file], use_dataset=False)
    assert len(fails) == 1
    assert "bad.ttl" in str(fails[0][0])
    assert graph is not None


def test_load_graphs_with_invalid_date_set_flag(sample_data_ttl, tmp_path):
    bad_file = tmp_path / "bad.unknown"
    bad_file.write_text("not rdf")
    ds, fails = load_graphs([sample_data_ttl, bad_file], use_dataset=True)
    assert len(fails) == 1
    assert ds is not None

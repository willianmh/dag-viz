import pytest
import pandas as pd
from components.graph import Graph
from components.cytoscape import Element, Elements, Node, Edge

@pytest.fixture
def sample_data():
    nodes_data = {
        "id": ["A", "B", "C", "D"],
        "label": ["A", "B", "C", "D"],
        "node_type": ["type1", "type2", "type1", "type2"],
        "parent": ["", "A", "A", "B"],
        "location": ["loc1", "loc2", "loc1", "loc2"]
    }
    edges_data = {
        "id": ["A->B", "A->C", "B->D", "C->D"],
        "source": ["A", "A", "B", "C"],
        "target": ["B", "C", "D", "D"]
    }
    nodes = pd.DataFrame(nodes_data)
    edges = pd.DataFrame(edges_data)
    return nodes, edges

def test_graph_initialization(sample_data):
    nodes, edges = sample_data
    graph = Graph(nodes, edges)
    assert graph.nodes.equals(nodes)
    assert graph.edges.equals(edges)
    assert graph.g is not None
    assert len(graph.complete_paths) > 0
    assert len(graph.mapping_node_to_path) > 0

def test_graph_from_elements(sample_data):
    nodes, edges = sample_data
    elements = Elements(
        elements=[
            Element(data=Node(**node)) for _, node in nodes.iterrows()
        ] + [
            Element(data=Edge(**edge)) for _, edge in edges.iterrows()
        ]
    )
    graph = Graph.from_elements(elements)
    assert graph.complete_paths == [["A", "B", "D"], ["A", "C", "D"]]

    assert graph.nodes["id"].equals(nodes["id"])
    assert graph.edges.equals(edges)

def test_compute_complete_paths(sample_data):
    nodes, edges = sample_data
    graph = Graph(nodes, edges)
    complete_paths = graph.compute_complete_paths()
    assert len(complete_paths) > 0

def test_map_node_to_paths(sample_data):
    nodes, edges = sample_data
    graph = Graph(nodes, edges)
    mapping = graph.map_node_to_paths()
    assert len(mapping) == len(nodes)

def test_select_related_elements(sample_data):
    # nodes, edges = sample_data
    # graph = Graph(nodes, edges)
    # selected_locations = ["loc1"]
    # new_graph = graph.select_related_elements(selected_locations, copy=True)
    # assert new_graph is not None
    # assert new_graph.nodes["location"].isin(selected_locations).all()
    pass

def test_group_by(sample_data):
    # nodes, edges = sample_data
    # graph = Graph(nodes, edges)
    # new_graph = graph.group_by("location", "type1", copy=True)
    # assert new_graph is not None
    # assert "loc1" in new_graph.nodes["id"].values
    # assert "loc2" in new_graph.nodes["id"].values
    pass
import pytest
import pandas as pd
from components.cytoscape import Node, Edge, Element, Elements


def test_nodes_from_dataframe():
    nodes_data = {
        "id": ["1", "2"],
        "label": ["Node 1", "Node 2"],
        "node_type": ["Type 1", "Type 2"],
        "location": ["Location 1", "Location 2"],
        "parent": ["Parent 1", "Parent 2"],  # Add this line
    }

    nodes_df = pd.DataFrame(nodes_data)
    nodes = Elements.nodes_from_dataframe(nodes_df)

    assert len(nodes) == 2
    assert nodes[0]["data"]["id"] == "1"
    assert nodes[0]["data"]["label"] == "Node 1"
    assert nodes[1]["data"]["id"] == "2"
    assert nodes[1]["data"]["label"] == "Node 2"


def test_edges_from_dataframe():
    edges_data = {"id": ["1", "2"], "source": ["1", "2"], "target": ["2", "3"]}
    edges_df = pd.DataFrame(edges_data)
    edges = Elements.edges_from_dataframe(edges_df)

    assert len(edges) == 2
    assert edges[0]["data"]["id"] == "1"
    assert edges[0]["data"]["source"] == "1"
    assert edges[0]["data"]["target"] == "2"
    assert edges[1]["data"]["id"] == "2"
    assert edges[1]["data"]["source"] == "2"
    assert edges[1]["data"]["target"] == "3"


def test_from_dataframe():
    nodes_data = {
        "id": ["1", "2"],
        "label": ["Node 1", "Node 2"],
        "node_type": ["Type 1", "Type 2"],
        "location": ["Location 1", "Location 2"],
        "parent": ["Parent 1", "Parent 2"],  # Add this line
    }
    edges_data = {"id": ["1", "2"], "source": ["1", "2"], "target": ["2", "3"]}
    nodes_df = pd.DataFrame(nodes_data)
    edges_df = pd.DataFrame(edges_data)

    elements = Elements.from_dataframe(nodes_df, edges_df).model_dump()

    assert len(elements["elements"]) == 4

    assert elements["num_nodes"] == 2
    assert elements["num_edges"] == 2

    assert elements["elements"][0]["data"]["id"] == "1"
    assert elements["elements"][1]["data"]["id"] == "2"
    assert elements["elements"][2]["data"]["id"] == "1"
    assert elements["elements"][3]["data"]["id"] == "2"


# def test_nodes2dict():
#     nodes_data = {
#         'id': ['1', '2'],
#         'label': ['Node 1', 'Node 2']
#     }
#     nodes_df = pd.DataFrame(nodes_data)
#     elements = Elements.from_dataframe(nodes_df, pd.DataFrame())

#     nodes_dict = elements.nodes2dict()

#     assert len(nodes_dict) == 2
#     assert nodes_dict[0]['data']['id'] == '1'
#     assert nodes_dict[0]['data']['label'] == 'Node 1'
#     assert nodes_dict[1]['data']['id'] == '2'
#     assert nodes_dict[1]['data']['label'] == 'Node 2'

# def test_edges2dict():
# edges_data = {
#     'id': ['1', '2'],
#     'source': ['1', '2'],
#     'target': ['2', '3']
# }
# edges_df = pd.DataFrame(edges_data)
# elements = Elements.from_dataframe(pd.DataFrame(), edges_df)

# edges_dict = elements.edges2dict()

# assert len(edges_dict) == 2
# assert edges_dict[0]['data']['id'] == '1'
# assert edges_dict[0]['data']['source'] == '1'
# assert edges_dict[0]['data']['target'] == '2'
# assert edges_dict[1]['data']['id'] == '2'
# assert edges_dict[1]['data']['source'] == '2'
# assert edges_dict[1]['data']['target'] == '3'

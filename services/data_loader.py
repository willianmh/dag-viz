import pandas as pd
from components.cytoscape import Elements
from components.graph import Graph


def load_data():
    nodes = pd.read_csv("data/nodes.csv")
    edges = pd.read_csv("data/edges.csv")

    nodes = _node_validator(nodes)
    edges = _edge_validator(edges)

    elements = Elements.from_dataframe(nodes, edges)
    return {
        "elements": elements,
        "types": nodes["node_type"].unique(),
        "locations": nodes["location"].unique(),
    }


def _node_validator(nodes: pd.DataFrame) -> pd.DataFrame:
    _nodes = nodes.copy()
    _nodes["label"] = _nodes["id"]
    _nodes["node_type"] = _nodes["node_type"]
    _nodes["parent"] = _nodes["parent"]
    _nodes["location"] = _nodes["location"]
    return _nodes[["id", "label", "node_type", "parent", "location"]]


def _edge_validator(edges: pd.DataFrame) -> pd.DataFrame:
    _edges = edges.copy()
    _edges["id"] = _edges["source"] + "->" + _edges["target"]
    _edges["source"] = _edges["source"]
    _edges["target"] = _edges["target"]
    return _edges[["id", "source", "target"]]

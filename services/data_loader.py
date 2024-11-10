import pandas as pd
from components.cytoscape import Edge, Elements, Node
from components.graph import Graph


def load_data():
    nodes = pd.read_csv("data/nodes.csv")
    edges = pd.read_csv("data/edges.csv")

    nodes = Node.node_validator(nodes)
    edges = Edge.edge_validator(edges)

    elements = Elements.from_dataframe(nodes, edges)
    return {
        "elements": elements,
        "types": nodes["node_type"].unique(),
        "locations": nodes["location"].unique(),
    }


def build_node_structure():
    nodes = pd.read_csv("data/nodes.csv")

    # initialize workspaces
    workspaces = nodes["workspace", "workspace_label"].unique()
    workspaces = workspaces.rename(columns={"workspace": "id", "workspace_label": "label"})
    

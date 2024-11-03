import networkx as nx
import pandas as pd
import plotly.express as px

from components.cytoscape import Edge, Elements, Node


class Graph:
    def __init__(self, nodes, edges):
        self.nodes: pd.DataFrame = nodes
        self.edges: pd.DataFrame = edges

        self._g = nx.from_pandas_edgelist(
            edges, "source", "target", create_using=nx.DiGraph()
        )

        self.nodes["is_leaf"] = self.nodes["id"].apply(
            lambda x: len(list(self._g.successors(x))) == 0
        )
        self.nodes["is_root"] = self.nodes["id"].apply(
            lambda x: len(list(self._g.predecessors(x))) == 0
        )

        self.edges["id"] = self.edges.apply(
            lambda x: f"{x['source']}->{x['target']}", axis=1
        )

        # iterate over the nodes and add the attributes to the graph
        for node, attrs in self._g.nodes(data=True):
            attrs.update(nodes[nodes["id"] == node].squeeze().to_dict())

        self._paths = self._compute_complete_paths()
        self._node_to_paths = self._map_node_to_paths()

        self._colors = self._index_colors(self.nodes)

    @classmethod
    def from_elements(cls, elements: Elements):
        nodes = pd.DataFrame(
            [
                node.data.model_dump()
                for node in elements.elements
                if isinstance(node.data, Node)
            ]
        )
        edges = pd.DataFrame(
            [
                edge.data.model_dump()
                for edge in elements.elements
                if isinstance(edge.data, Edge)
            ]
        )

        return cls(nodes, edges)

    def _index_colors(self, nodes: pd.DataFrame):
        color_map = px.colors.qualitative.Plotly
        node_types = nodes["node_type"].unique()

        return dict(zip(node_types, color_map[: len(node_types)]))

    def _compute_complete_paths(self) -> list:
        complete_paths = []
        _roots = self.nodes[self.nodes["is_root"]]["id"]
        _leaves = self.nodes[self.nodes["is_leaf"]]["id"]

        for root in _roots:
            for leaf in _leaves:
                if root != leaf:
                    try:
                        paths = list(
                            nx.all_simple_paths(self._g, source=root, target=leaf)
                        )
                        complete_paths.extend(paths)
                    except nx.NetworkXNoPath:
                        continue

        return complete_paths

    def _map_node_to_paths(self) -> dict:
        node_to_paths = {}
        for node in self._g.nodes():
            node_to_paths[node] = [path for path in self._paths if node in path]
        return node_to_paths

    def _export_elements(self, nodes: pd.DataFrame, edges: pd.DataFrame) -> Elements:
        return Elements.from_dataframe(nodes, edges)

    def _transform_nodes(self, nodes: pd.DataFrame) -> pd.DataFrame:
        _nodes = nodes.copy()
        _nodes["label"] = _nodes["id"]
        _nodes["node_type"] = _nodes["node_type"]
        _nodes["parent"] = _nodes["parent"]
        _nodes["location"] = _nodes["location"]
        return _nodes[["id", "label", "node_type", "parent", "location"]]

    def _transform_edges(self, edges: pd.DataFrame) -> pd.DataFrame:
        _edges = edges.copy()
        _edges["id"] = _edges["source"] + "->" + _edges["target"]
        _edges["source"] = _edges["source"]
        _edges["target"] = _edges["target"]
        return _edges[["id", "source", "target"]]

    def export_elements(self) -> Elements:
        _nodes = self._transform_nodes(self.nodes)
        _edges = self._transform_edges(self.edges)

        return self._export_elements(_nodes, _edges)

    def select_elements(self, selected_types, selected_locations) -> list:
        # TODO: Implement this method
        filtered_nodes = self.nodes[
            [
                node["node_type"] in selected_types
                and node["location"] in selected_locations
                for idx, node in self.nodes.iterrows()
            ]
        ]

        filtered_edges = self.edges[
            self.edges["source"].isin(filtered_nodes["id"])
            & self.edges["target"].isin(filtered_nodes["id"])
        ]

        return self._export_elements(filtered_nodes, filtered_edges)

    def select_related_elements(self, selected_locations) -> Elements:
        filtered_nodes = self.nodes[
            [
                node["location"] in selected_locations
                for idx, node in self.nodes.iterrows()
            ]
        ]

        # Get the list of nodes and edges to highlight
        nodes_to_filtered = set()
        edges_to_filtered = set()

        # Find all paths that include the selected node
        for node_id in filtered_nodes["id"]:
            paths = self._node_to_paths.get(node_id, [])

            for path in paths:
                nodes_to_filtered.update(path)
                edges_in_path = list(zip(path[:-1], path[1:]))
                edges_to_filtered.update(edges_in_path)

        related_nodes = self.nodes[self.nodes["id"].isin(nodes_to_filtered)]

        related_edges = self.edges[
            self.edges["source"].isin(nodes_to_filtered)
            & self.edges["target"].isin(nodes_to_filtered)
        ]

        _nodes = self._transform_nodes(related_nodes)
        _edges = self._transform_edges(related_edges)
        return self._export_elements(_nodes, _edges)

    def group_by(self, group_by: str, node_type: str) -> dict:
        # transform nodes to group_by if node_type is met
        _grouped_nodes = self.nodes.copy()
        _grouped_nodes["id"] = _grouped_nodes[group_by].where(
            _grouped_nodes["node_type"] == node_type, _grouped_nodes["id"]
        )

        # remove duplicates
        _grouped_nodes = _grouped_nodes.drop_duplicates(subset=["id"])

        # transform nodes in edges to group_by if node_type is met
        _grouped_edges = self.edges.copy()
        _grouped_edges["source"] = _grouped_edges["source"].map(
            lambda x: (
                self.nodes[self.nodes["id"] == x][group_by].values[0]
                if self.nodes[self.nodes["id"] == x]["node_type"].values[0] == node_type
                else x
            )
        )

        _grouped_edges["target"] = _grouped_edges["target"].map(
            lambda x: (
                self.nodes[self.nodes["id"] == x][group_by].values[0]
                if self.nodes[self.nodes["id"] == x]["node_type"].values[0] == node_type
                else x
            )
        )
        _grouped_edges["id"] = (
            _grouped_edges["source"] + "->" + _grouped_edges["target"]
        )

        # remove duplicates
        _grouped_edges = _grouped_edges.drop_duplicates(subset=["id"])
        # remove edges that have the same source and target
        _grouped_edges = _grouped_edges[
            _grouped_edges["source"] != _grouped_edges["target"]
        ]

        _nodes = self._transform_nodes(_grouped_nodes)
        _edges = self._transform_edges(_grouped_edges)
        return self._export_elements(_nodes, _edges)

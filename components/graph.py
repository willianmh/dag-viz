from typing import Self
import networkx as nx
import pandas as pd
import plotly.express as px

from components.cytoscape import Edge, Elements, Node


class Graph:
    def __init__(self, nodes: pd.DataFrame, edges: pd.DataFrame):
        self.nodes: pd.DataFrame = nodes
        self.edges: pd.DataFrame = edges

        self.g = None
        self.complete_paths = []
        self.mapping_node_to_path = {}
        self._colors = {}
        self._calculate_graph_properties()

    def _calculate_graph_properties(self):
        self.g = nx.from_pandas_edgelist(
            self.edges, "source", "target", create_using=nx.DiGraph()
        )
        #remove the is_leaf and is_root columns if they exist
        if "is_leaf" in self.nodes.columns:
            self.nodes.drop(columns=["is_leaf"], inplace=True)
        if "is_root" in self.nodes.columns:
            self.nodes.drop(columns=["is_root"], inplace=True)

        self.nodes["is_leaf"] = self.nodes["id"].apply(
            lambda x: len(list(self.g.successors(x))) == 0
        )
        self.nodes["is_root"] = self.nodes["id"].apply(
            lambda x: len(list(self.g.predecessors(x))) == 0
        )

        self.edges["id"] = self.edges.apply(
            lambda x: f"{x['source']}->{x['target']}", axis=1
        )


        # iterate over the nodes and add the attributes to the graph
        for node, attrs in self.g.nodes(data=True):
            attrs.update(self.nodes[self.nodes["id"] == node].squeeze().to_dict())

        self.complete_paths = self.compute_complete_paths()
        self.mapping_node_to_path = self.map_node_to_paths()

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

    def compute_complete_paths(self) -> list:
        # TODO: receive only g as argument, nodes can be accessed from g.nodes()
        complete_paths = []
        _roots = self.nodes[self.nodes["is_root"]]["id"]
        _leaves = self.nodes[self.nodes["is_leaf"]]["id"]

        for root in _roots:
            for leaf in _leaves:
                if root != leaf:
                    try:
                        paths = list(
                            nx.all_simple_paths(self.g, source=root, target=leaf)
                        )
                        complete_paths.extend(paths)
                    except nx.NetworkXNoPath:
                        continue

        return complete_paths

    def map_node_to_paths(self) -> dict:
        node_to_paths = {}
        for node in self.nodes["id"]:
            node_to_paths[node] = [path for path in self.complete_paths if node in path]
        return node_to_paths
    
    def _modify_graph(func):
        """
        Decorator to wrap methods that modify the graph, ensuring properties are recalculated.
        """
        def wrapper(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            # Only recalculate if the modification is performed on the current instance
            if not kwargs.get('copy', False):
                self._calculate_graph_properties()
            return result
        return wrapper

    def _index_colors(self, nodes: pd.DataFrame) -> dict:
        color_map = px.colors.qualitative.Plotly
        node_types = nodes["node_type"].unique()

        return dict(zip(node_types, color_map[: len(node_types)]))

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

    @_modify_graph
    def select_related_elements(self, selected_locations: list, copy=False) -> Self:
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
            paths = self.mapping_node_to_path.get(node_id, [])

            for path in paths:
                nodes_to_filtered.update(path)
                edges_in_path = list(zip(path[:-1], path[1:]))
                edges_to_filtered.update(edges_in_path)

        related_nodes = self.nodes[self.nodes["id"].isin(nodes_to_filtered)]
        related_nodes = related_nodes.copy()

        related_edges = self.edges[
            self.edges["source"].isin(nodes_to_filtered)
            & self.edges["target"].isin(nodes_to_filtered)
        ]
        related_edges = related_edges.copy()

        if copy:
            # Return a new instance of Graph with updated nodes
            # new_graph = Graph(nodes=related_nodes[["id", "label", "node_type", "parent", "location"]], edges=related_edges)
            new_graph = Graph(related_nodes, related_edges)
            return new_graph
        else:
            # Modify the current instance
            self.nodes = related_nodes
            self.edges = related_edges
            # Note: Edges might need re-evaluation depending on how grouping affects connectivity
        return None

    @_modify_graph
    def group_by(self, group_by: str, node_type: str, copy=False) -> dict:
        # transform nodes to group_by if node_type is met
        _grouped_nodes = self.nodes.copy()
        _grouped_nodes["id"] = _grouped_nodes[group_by].where(
            _grouped_nodes["node_type"] == node_type, _grouped_nodes["id"]
        )

        # remove duplicates
        _grouped_nodes = _grouped_nodes.drop_duplicates(subset=["id"])
        _grouped_nodes = _grouped_nodes.copy()

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
        _grouped_edges = _grouped_edges.copy()
        

        if copy:
            # Return a new instance of Graph with updated nodes
            new_graph = Graph(nodes=_grouped_nodes, edges=_grouped_edges)
            return new_graph
        else:
            # Modify the current instance
            self.nodes = _grouped_nodes
            self.edges = _grouped_edges
            # Note: Edges might need re-evaluation depending on how grouping affects connectivity
        return None

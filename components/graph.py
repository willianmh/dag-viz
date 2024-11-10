from typing import Self
import networkx as nx
import pandas as pd
import plotly.express as px

from components.cytoscape import Edge, Element, Elements, Node
from components.nodes_model import Nodes


class Graph:
    def __init__(
        self,
        nodes: pd.DataFrame,
        edges: pd.DataFrame,
        clusters: Nodes = None,
    ):
        self.nodes: pd.DataFrame = nodes
        self.edges: pd.DataFrame = edges
        self.clusters: dict = clusters

        self.g = None
        self.complete_paths = []
        self.mapping_node_to_path = {}
        self._colors = {}
        self._calculate_graph_properties()

    def _calculate_graph_properties(self):
        self.g = nx.from_pandas_edgelist(
            self.edges, "source", "target", create_using=nx.DiGraph()
        )
        # remove the is_leaf and is_root columns if they exist
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
    def from_model(cls, model: Nodes):
        clusters = {
            "workspace": [],
            "dataset": [],
            "report": [],
            "table": [],
            "page": [],
        }
        nodes = []
        for workspace in model.workspaces:
            clusters["workspace"].append(workspace.model_dump(exclude_none=True))
            for dataset_or_report in workspace.children:
                clusters[dataset_or_report.type].append(
                    dataset_or_report.model_dump(exclude_none=True)
                )
                for table_or_page in dataset_or_report.children:
                    clusters[table_or_page.type].append(
                        table_or_page.model_dump(exclude_none=True)
                    )
                    for visual_or_measure in table_or_page.children:
                        nodes.append(
                            {
                                **visual_or_measure.model_dump(exclude_none=True),
                                "page": table_or_page.id if table_or_page.type == "page" else None,
                                "table": table_or_page.id if table_or_page.type == "table" else None,
                                "report": dataset_or_report.id if dataset_or_report.type == "report" else None,
                                "dataset": dataset_or_report.id if dataset_or_report.type == "dataset" else None,
                                "workspace": workspace.id,
                            }
                        )

        nodes = pd.DataFrame(nodes)

        edges = []
        for edge in model.edges:
            edges.append(edge.model_dump(exclude_none=True)
                         )
            
        edges = pd.DataFrame(edges)
        return cls(nodes, edges, clusters)

    @classmethod
    def from_elements(cls, elements: Elements):
        nodes = pd.DataFrame(
            [
                element.data.model_dump()
                for element in elements.elements
                if isinstance(element.data, Node) and element.data.type in ["measure", "visual"]
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
            if not kwargs.get("copy", False):
                self._calculate_graph_properties()
            return result

        return wrapper

    def _index_colors(self, nodes: pd.DataFrame) -> dict:
        color_map = px.colors.qualitative.Plotly
        types = nodes["type"].unique()

        return dict(zip(types, color_map[: len(types)]))

    def _export_elements(self, nodes: pd.DataFrame, edges: pd.DataFrame) -> Elements:
        return Elements.from_dataframe(nodes, edges)

    def _transform_nodes(self, nodes: pd.DataFrame) -> pd.DataFrame:
        return Node.node_validator(nodes).copy()

    def _transform_edges(self, edges: pd.DataFrame) -> pd.DataFrame:
        return Edge.edge_validator(edges).copy()

    def export_elements(self) -> Elements:
        clusters = []
        for k, v in self.clusters.items():
            for item in v:
                clusters.append(
                    Element(
                        data=Node.from_dict(item),
                        classes=k,
                        _type="cluster",
                    )
                )

        _nodes = self._transform_nodes(self.nodes)
        _edges = self._transform_edges(self.edges)

        nodes_elements = Elements.nodes_from_dataframe(_nodes)
        edges_elements = Elements.edges_from_dataframe(_edges)

        elements = clusters + nodes_elements + edges_elements
        return Elements(elements=elements)

    def select_elements(self, selected_types, selected_locations) -> list:
        # TODO: Implement this method
        filtered_nodes = self.nodes[
            [
                node["type"] in selected_types
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
    def select_related_elements(self, selected_cluster: str, selected_values: list, copy=False) -> Self:
        # get cluster data
        df = pd.DataFrame(self.clusters[selected_cluster]).rename(columns={"id": selected_cluster, "label": f"{selected_cluster}_label"})
        
        merged_nodes = self.nodes.merge(df[[selected_cluster, f"{selected_cluster}_label"]], left_on=selected_cluster, right_on=selected_cluster, how="left")
        

        filtered_nodes = merged_nodes[
            [
                node[f"{selected_cluster}_label"] in selected_values
                for idx, node in merged_nodes.iterrows()
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
            # new_graph = Graph(nodes=related_nodes[["id", "label", "type", "source", "location"]], edges=related_edges)
            new_graph = Graph(related_nodes, related_edges, self.clusters)
            return new_graph
        else:
            # Modify the current instance
            self.nodes = related_nodes
            self.edges = related_edges
            self.clusters = self.clusters
            # Note: Edges might need re-evaluation depending on how grouping affects connectivity
        return None

    @_modify_graph
    def group_by(self, group_by: str, type: str, copy=False) -> dict:
        # get cluster data
        df = pd.DataFrame(self.clusters[group_by]).rename(columns={"id": group_by, "label": f"{group_by}_label", "parent": f"{group_by}_parent"})
        
        # transform nodes to group_by if type is met
        merged_nodes = self.nodes.merge(df[[group_by, f"{group_by}_label", f"{group_by}_parent"]], left_on=group_by, right_on=group_by, how="left")
        
        _grouped_nodes = merged_nodes.copy()
        # TODO: type can be replaced by not nan
        _grouped_nodes["id"] = merged_nodes[group_by].where(
            merged_nodes["type"] == type, merged_nodes["id"]
        )
        _grouped_nodes["label"] = _grouped_nodes[f"{group_by}_label"].where(
            _grouped_nodes["type"] == type, _grouped_nodes["label"]
        )
        _grouped_nodes["parent"] = _grouped_nodes[f"{group_by}_parent"].where(
            _grouped_nodes["type"] == type, _grouped_nodes["parent"]
        )

        # remove duplicates
        _grouped_nodes = _grouped_nodes.drop_duplicates(subset=["id"])
        _grouped_nodes = _grouped_nodes.copy()

        # transform nodes in edges to group_by if type is met
        _grouped_edges = self.edges.copy()
        _grouped_edges["source"] = _grouped_edges["source"].map(
            lambda x: (
                merged_nodes[merged_nodes["id"] == x][group_by].values[0]
                if merged_nodes[merged_nodes["id"] == x]["type"].values[0] == type
                else x
            )
        )

        _grouped_edges["target"] = _grouped_edges["target"].map(
            lambda x: (
                merged_nodes[merged_nodes["id"] == x][group_by].values[0]
                if merged_nodes[merged_nodes["id"] == x]["type"].values[0] == type
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

        # remove extra clusters
        clusters = self.clusters
        clusters.pop(group_by)

        if copy:
            # Return a new instance of Graph with updated nodes
            new_graph = Graph(nodes=_grouped_nodes, edges=_grouped_edges, clusters=clusters)
            return new_graph
        else:
            # Modify the current instance
            self.nodes = _grouped_nodes
            self.edges = _grouped_edges
            self.clusters = clusters
            # Note: Edges might need re-evaluation depending on how grouping affects connectivity
        return None

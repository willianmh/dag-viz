from enum import Enum
from pydantic import BaseModel, computed_field
from dataclasses import dataclass, asdict
from typing import List, Optional, Union

import pandas as pd

from components.nodes_model import Nodes


class Node(BaseModel):
    id: str
    label: str
    type: str
    parent: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict):
        # check if data is a dictionary
        if not isinstance(data, dict):
            raise ValueError("data must be a dictionary")

        # check if data has the required keys
        required_keys = ["id", "label", "type"]
        if not all(key in data for key in required_keys):
            raise ValueError(
                f"data must have the following keys: {', '.join(required_keys)}"
            )
        
        return cls(
            id=data["id"],
            label=data["label"],
            type=data["type"],
            parent=data.get("parent", None),
        )
    
    def to_cytoscape(self):
        return {
            "data": self.model_dump(exclude_none=True),
            "classes": self.type,
        }

    @staticmethod
    def node_validator(nodes: pd.DataFrame) -> pd.DataFrame:
        return nodes[
            [
                "id",
                "label",
                "type",
                "parent",
            ]
        ]


class Edge(BaseModel):
    id: str
    source: str
    target: str

    def to_cytoscape(self):
        return {
            "data": self.model_dump(exclude_none=True),
        }

    @staticmethod
    def edge_validator(edges: pd.DataFrame) -> pd.DataFrame:
        edges["id"] = edges["source"] + "->" + edges["target"]
        return edges[["id", "source", "target"]]


class Element(BaseModel):
    data: Union[Node, Edge]
    classes: Optional[str] = None
    _type: Optional[str] = None


class Elements(BaseModel):
    elements: List[Element]

    @computed_field
    @property
    def num_nodes(self) -> int:
        return len([el for el in self.elements if isinstance(el.data, Node)])

    @computed_field
    @property
    def num_edges(self) -> int:
        return len([el for el in self.elements if isinstance(el.data, Edge)])

    @classmethod
    def from_model(cls, model: Nodes):
        model_dict = model.model_dump(exclude_none=True)
        # add workspaces
        workspaces = [
            Element(
                data=Node.from_dict(workspace),
                classes=workspace["type"],
                _type = "cluster"
            )
            for workspace in model_dict["workspaces"]
        ]

        # add datasets and reports
        datasets_and_reports = []
        tables_and_pages = []
        measures_and_visuals = []
        for workspace in model_dict["workspaces"]:
            for dataset_or_report in workspace["children"]:
                datasets_and_reports.append(
                    Element(
                        data=Node.from_dict(dataset_or_report), 
                        classes=dataset_or_report["type"],
                        _type = "cluster"
                    )
                )

                # add tables and pages
                for table_or_page in dataset_or_report["children"]:
                    tables_and_pages.append(
                        Element(
                            data=Node.from_dict(table_or_page),
                            classes=table_or_page["type"],
                            _type = "cluster"
                            )
                    )

                    # add measures and visuals
                    for measure_or_visual in table_or_page["children"]:
                        measures_and_visuals.append(
                            Element(
                                data=Node.from_dict(measure_or_visual),
                                classes=measure_or_visual["type"],
                                _type = "nodes"
                            )
                        )
        

        edges = model_dict["edges"]
        edges_elements = [
            Element(
                data=Edge(**edge),
                classes="edge"
                )
                for edge in edges
            ]

        _elements = workspaces + datasets_and_reports + tables_and_pages + measures_and_visuals + edges_elements
        return cls(elements=_elements)

    @classmethod
    def from_dataframe(cls, nodes: pd.DataFrame, edges: pd.DataFrame):

        nodes_elements = cls.nodes_from_dataframe(nodes)
        edges_elements = cls.edges_from_dataframe(edges)

        _elements = nodes_elements + edges_elements

        return cls(elements=_elements)

    @staticmethod
    def nodes_from_dataframe(nodes: pd.DataFrame) -> List[dict]:
        return [
            Element(
                data=Node(**node),
                classes=node["type"],
                _type = "nodes"
            )
            for _, node in nodes.iterrows()
        ]

    @staticmethod
    def edges_from_dataframe(edges: pd.DataFrame) -> List[dict]:
        return [
            Element(
                data=Edge(**edge), 
                classes="edge"
            )
            for _, edge in edges.iterrows()
        ]

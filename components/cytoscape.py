from enum import Enum
from pydantic import BaseModel, computed_field
from dataclasses import dataclass, asdict
from typing import List, Optional, Union

import pandas as pd


class NodeTypeEnum(Enum):
    MEASURE: str = "measure"
    DIMENSION: str = "dimension"


class Group(BaseModel):
    id: str
    label: str


class SubGroup(BaseModel):
    id: str
    label: str
    parent: str


class Node(BaseModel):
    id: str
    label: str
    node_type: str
    source: str
    source_label: str
    location: str
    location_label: str
    workspace: str
    workspace_label: str

    @staticmethod
    def node_validator(nodes: pd.DataFrame) -> pd.DataFrame:
        return nodes[
            [
                "id",
                "label",
                "node_type",
                "source",
                "source_label",
                "location",
                "location_label",
                "workspace",
                "workspace_label",
            ]
        ]


class Edge(BaseModel):
    id: str
    source: str
    target: str

    @staticmethod
    def edge_validator(edges: pd.DataFrame) -> pd.DataFrame:
        edges["id"] = edges["source"] + "->" + edges["target"]
        return edges[["id", "source", "target"]]


class Element(BaseModel):
    data: Union[Group, SubGroup, Node, Edge]
    classes: Optional[str] = None


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
    def from_dataframe(cls, nodes: pd.DataFrame, edges: pd.DataFrame):
        subgroups_df = (
            nodes[["source", "source_label", "location"]]
            .drop_duplicates()
            .rename(
                columns={"source": "id", "source_label": "label", "location": "parent"}
            )
            .copy()
        )
        groups_df = (
            nodes[["location", "location_label"]]
            .drop_duplicates()
            .rename(columns={"location": "id", "location_label": "label"})
            .copy()
        )

        nodes_elements = cls.nodes_from_dataframe(nodes)
        edges_elements = cls.edges_from_dataframe(edges)

        subgroups = [
            {
                "data": SubGroup(**subgroup).model_dump(exclude_none=True),
                "classes": "subgroup",
            }
            for _, subgroup in subgroups_df.iterrows()
        ]
        groups = [
            {"data": Group(**group).model_dump(exclude_none=True), "classes": "group"}
            for _, group in groups_df.iterrows()
        ]

        _elements = groups + subgroups + nodes_elements + edges_elements

        return cls(elements=_elements)

    @staticmethod
    def nodes_from_dataframe(nodes: pd.DataFrame) -> List[dict]:
        return [
            {"data": Node(**node).model_dump(exclude_none=True)}
            for _, node in nodes.iterrows()
        ]

    @staticmethod
    def edges_from_dataframe(edges: pd.DataFrame) -> List[dict]:
        return [
            {"data": Edge(**edge).model_dump(exclude_none=True)}
            for _, edge in edges.iterrows()
        ]

from pydantic import BaseModel, computed_field
from dataclasses import dataclass, asdict
from typing import List, Union

import pandas as pd


class Node(BaseModel):
    id: str
    label: str
    node_type: str
    parent: str
    location: str


class Edge(BaseModel):
    id: str
    source: str
    target: str


class Element(BaseModel):
    data: Union[Node, Edge]


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
        nodes = cls.nodes_from_dataframe(nodes)
        edges = cls.edges_from_dataframe(edges)

        _elements = nodes + edges

        return cls(elements=_elements)

    # def nodes2dict(self) -> List[dict]:
    #     _nodes = [
    #         {
    #             "data": n.dict()
    #         }
    #         for n in self.nodes
    #     ]
    #     return _nodes

    # def edges2dict(self) -> List[dict]:
    #     _edges = [
    #         {
    #             "data": e.dict()
    #         }
    #         for e in self.edges
    #     ]
    #     return _edges

    @staticmethod
    def nodes_from_dataframe(nodes: pd.DataFrame) -> List[dict]:
        return [
            {"data": Node(**node).model_dump(exclude_none=True)}
            for idx, node in nodes.iterrows()
        ]

    @staticmethod
    def edges_from_dataframe(edges: pd.DataFrame) -> List[dict]:
        return [
            {"data": Edge(**edge).model_dump(exclude_none=True)}
            for idx, edge in edges.iterrows()
        ]

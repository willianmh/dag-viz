from typing import List, Union
from pydantic import BaseModel


class Measure(BaseModel):
    id: str
    label: str
    type: str
    parent: str


class Visual(BaseModel):
    id: str
    label: str
    type: str
    parent: str


class Page(BaseModel):
    id: str
    label: str
    type: str
    parent: str
    children: List[Visual]


class Table(BaseModel):
    id: str
    label: str
    type: str
    parent: str
    children: List[Measure]


class Report(BaseModel):
    id: str
    label: str
    type: str
    parent: str
    children: List[Page]


class Dataset(BaseModel):
    id: str
    label: str
    type: str
    parent: str
    children: List[Table]


class Workspace(BaseModel):
    id: str
    label: str
    type: str
    children: List[Union[Dataset, Report]]


class Edge(BaseModel):
    id: str
    source: str
    target: str


class Nodes(BaseModel):
    workspaces: List[Workspace]
    edges: List[Edge]
    
    def get_reports(self):
        return [report for workspace in self.workspaces for report in workspace.children if isinstance(report, Report)]
    
    def get_datasets(self):
        return [dataset for workspace in self.workspaces for dataset in workspace.children if isinstance(dataset, Dataset)]
    
    def get_tables(self):
        return [table for dataset in self.get_datasets() for table in dataset.children]
    
    def get_pages(self):
        return [page for report in self.get_reports() for page in report.children]
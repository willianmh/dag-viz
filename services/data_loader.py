import pandas as pd
from components.cytoscape import Edge, Elements, Node
from components.graph import Graph
from components.nodes_model import Dataset, Measure, Nodes, Page, Report, Table, Visual, Workspace


def build_node_structure(df):
    # Dictionaries to hold unique instances
    workspaces = {}
    datasets = {}
    reports = {}
    tables = {}
    pages = {}

    # Group the data by workspace
    grouped = df.groupby(['workspace', 'workspace_label'])

    for (workspace_id, workspace_label), group in grouped:
        if workspace_id not in workspaces:
            workspaces[workspace_id] = {
                'id': workspace_id,
                'label': workspace_label,
                'type': 'workspace',
                'children_datasets': {},
                'children_reports': {}
            }
        
        for _, row in group.iterrows():
            node_type = row['node_type']
            location_id = row['location']
            location_label = row['location_label']
            source_id = row['source']
            source_label = row['source_label']
            
            if node_type == 'measure':
                # Measures belong to Tables, which belong to Datasets
                if location_id not in datasets:
                    datasets[location_id] = {
                        'id': location_id,
                        'label': location_label,
                        'type': 'dataset',
                        'parent': workspace_id,
                        'children_tables': {}
                    }
                    workspaces[workspace_id]['children_datasets'][location_id] = datasets[location_id]
                
                if source_id not in tables:
                    tables[source_id] = {
                        'id': source_id,
                        'label': source_label,
                        'type': 'table',
                        'parent': location_id,
                        'children_measures': {}
                    }
                    datasets[location_id]['children_tables'][source_id] = tables[source_id]
                
                # Add Measure
                measure_id = row['id']
                tables[source_id]['children_measures'][measure_id] = {
                    'id': measure_id,
                    'label': row['label'],
                    'type': 'measure',
                    'parent': source_id
                }
            
            elif node_type == 'visual':
                # Visuals belong to Pages, which belong to Reports
                if location_id not in reports:
                    reports[location_id] = {
                        'id': location_id,
                        'label': location_label,
                        'type': 'report',
                        'parent': workspace_id,
                        'children_pages': {}
                    }
                    workspaces[workspace_id]['children_reports'][location_id] = reports[location_id]
                
                if source_id not in pages:
                    pages[source_id] = {
                        'id': source_id,
                        'label': source_label,
                        'type': 'page',
                        'parent': location_id,
                        'children_visuals': {}
                    }
                    reports[location_id]['children_pages'][source_id] = pages[source_id]
                
                # Add Visual
                visual_id = row['id']
                pages[source_id]['children_visuals'][visual_id] = {
                    'id': visual_id,
                    'label': row['label'],
                    'type': 'visual',
                    'parent': source_id
                }

    return workspaces


def initialize_nodes(workspaces):
    nodes = []
    for workspace in workspaces.values():
        workspace_children = []
        
        # Add Datasets
        for dataset in workspace['children_datasets'].values():
            tables_list = []
            for table in dataset['children_tables'].values():
                measures_list = [Measure(**measure) for measure in table['children_measures'].values()]
                tables_list.append(Table(
                    id=table['id'],
                    label=table['label'],
                    type=table['type'],
                    parent=table['parent'],
                    children=measures_list
                ))
            
            dataset_model = Dataset(
                id=dataset['id'],
                label=dataset['label'],
                type=dataset['type'],
                parent=dataset['parent'],
                children=tables_list
            )
            workspace_children.append(dataset_model)
        
        # Add Reports
        for report in workspace['children_reports'].values():
            pages_list = []
            for page in report['children_pages'].values():
                visuals_list = [Visual(**visual) for visual in page['children_visuals'].values()]
                pages_list.append(Page(
                    id=page['id'],
                    label=page['label'],
                    type=page['type'],
                    parent=page['parent'],
                    children=visuals_list
                ))
            
            report_model = Report(
                id=report['id'],
                label=report['label'],
                type=report['type'],
                parent=report['parent'],
                children=pages_list
            )
            workspace_children.append(report_model)
        
        workspace_model = Workspace(
            id=workspace['id'],
            label=workspace['label'],
            type=workspace['type'],
            children=workspace_children
        )
        nodes.append(workspace_model)

    # Create the final Elements instance
    return nodes


def load_data():
    nodes_df = pd.read_csv("data/nodes.csv")
    edges_df = pd.read_csv("data/edges.csv")


    workspaces = build_node_structure(nodes_df)
    nodes = initialize_nodes(workspaces)

    edges = [
        {
            "id": edge["source"] + "->" + edge["target"],
            "source": edge["source"],
            "target": edge["target"],
        }
        for _, edge in edges_df.iterrows()
    ]

    model = Nodes(workspaces=nodes, edges=edges)

    return {
        "model": model,
        "types": nodes_df["node_type"].unique(),
        "datasets": [dataset.model_dump(exclude_none=True)["label"]for dataset in model.get_datasets()],
        "reports": [report.model_dump(exclude_none=True)["label"] for report in model.get_reports()],
        "tables": [table.model_dump(exclude_none=True)["label"] for table in model.get_tables()],
        "pages": [page.model_dump(exclude_none=True)["label"] for page in model.get_pages()],
    }
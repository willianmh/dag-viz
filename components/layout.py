from dash import html, dcc
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto

from assets.stylesheet import default_stylesheet, SIDEBAR_STYLE
from components.cytoscape import Elements
from components.nodes_model import Nodes
from services.data_loader import load_data

cyto.load_extra_layouts()


def get_filter_pane():
    initial_data = load_data()
    types = initial_data["types"]
    tables = initial_data["tables"]
    return html.Div(
        [
            html.Div(
                [
                    html.H2("Graph Explorer"),
                    html.Hr(),
                    html.P("Explore the graph by filtering nodes", className="lead"),
                    html.Div(
                        [
                            html.Label("Group Measures:"),
                            dcc.RadioItems(
                                id="group-measures",
                                options=[
                                    {
                                        "label": "by Dataset",
                                        "value": "dataset",
                                    },
                                    {
                                        "label": "by Table",
                                        "value": "table",
                                    },
                                    {
                                        "label": "by Measure",
                                        "value": "default",
                                    },
                                ],
                                value="default",
                                inline=True,
                            ),
                        ]
                    ),
                    html.Div(
                        [
                            html.Label("Group Visuals:"),
                            dcc.RadioItems(
                                id="group-visuals",
                                options=[
                                    {
                                        "label": "by Report",
                                        "value": "report",
                                    },
                                    {
                                        "label": "by Page",
                                        "value": "page",
                                    },
                                    {
                                        "label": "by Visual",
                                        "value": "default",
                                    },
                                ],
                                value="default",
                                inline=True,
                            ),
                        ]
                    ),
                ]
            ),
            html.Div(
                [
                    html.H2("Filters"),
                    html.Hr(),
                    html.P("A simple sidebar layout with filters", className="lead"),
                    dbc.Nav(
                        [
                            html.Div(
                                [
                                    html.Label("Filter by Type:"),
                                    dcc.Checklist(
                                        id="type-filter",
                                        options=[
                                            {"label": t.title(), "value": t}
                                            for t in types
                                        ],
                                        inline=True,
                                    ),
                                ]
                            ),
                            html.Div(
                                [
                                    html.Label("Filter by Table:"),
                                    dcc.Checklist(
                                        id="table-filter",
                                        options=[
                                            {"label": loc.title(), "value": loc}
                                            for loc in tables
                                        ],
                                        inline=True,
                                    ),
                                ]
                            ),
                        ],
                        vertical=True,
                        pills=True,
                    ),
                ]
            ),
        ],
        style=SIDEBAR_STYLE,
    )


def serve_layout():
    initial_data = load_data()
    model: Nodes = initial_data["model"]
    elements: dict = Elements.from_model(model).model_dump()["elements"]
    

    return html.Div(
        [
            dcc.Store(id="initial-data", data=model.model_dump(exclude_none=True), storage_type="memory"),
            dcc.Store(id="elements", data=elements, storage_type="memory"),
            dcc.Store(id="selected-node", data=None, storage_type="memory"),
            dbc.Row(
                [
                    dbc.Col(get_filter_pane()),
                    dbc.Col(
                        cyto.Cytoscape(
                            id="cytoscape",
                            elements=elements,
                            # style={'width': '100%', 'height': '600px'},
                            layout={
                                "name": "klay",
                                "rankDir": "LR",  # Left to Right
                                "nodeSep": 50,
                                "rankSep": 100,
                            },
                            stylesheet=default_stylesheet,
                            style={"width": "100%", "height": "600px"},
                        ),
                        width=9,
                        style={
                            "margin-left": "15px",
                            "margin-top": "7px",
                            "margin-right": "15px",
                        },
                    ),
                ]
            ),
        ]
    )

from dash import html, dcc
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto

from assets.stylesheet import default_stylesheet, SIDEBAR_STYLE
from services.data_loader import load_data

cyto.load_extra_layouts()


def get_filter_pane():
    initial_data = load_data()
    types = initial_data["types"]
    locations = initial_data["locations"]
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
                                        "value": "location",
                                    },
                                    {
                                        "label": "by Table",
                                        "value": "parent",
                                    },
                                ],
                                # value=selection,
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
                                        "value": "location",
                                    },
                                    {
                                        "label": "by Page",
                                        "value": "parent",
                                    },
                                ],
                                # value=locations,
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
                                        value=types,
                                        inline=True,
                                    ),
                                ]
                            ),
                            html.Div(
                                [
                                    html.Label("Filter by Location:"),
                                    dcc.Checklist(
                                        id="location-filter",
                                        options=[
                                            {"label": loc, "value": loc}
                                            for loc in locations
                                        ],
                                        value=locations,
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
    elements = initial_data["elements"].model_dump()["elements"]

    return html.Div(
        [
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

from dash.dependencies import Input, Output
from app import app
from components.cytoscape import Elements
from components.graph import Graph


@app.callback(
    Output("cytoscape", "elements", allow_duplicate=True),
    Input("location-filter", "value"),
    Input("elements", "data"),
    prevent_initial_call=True,
)
def update_related_elements(selected_locations, elements):
    if not selected_locations:
        return elements

    _elements = Elements(elements=elements)

    g = Graph.from_elements(_elements)
    new_elements = g.select_related_elements(selected_locations).model_dump()[
        "elements"
    ]

    return new_elements

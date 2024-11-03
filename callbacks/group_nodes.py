from dash.dependencies import Input, Output, State
from app import app
from components.cytoscape import Elements
from components.graph import Graph
from services.data_loader import load_data


@app.callback(
    Output("cytoscape", "elements", allow_duplicate=True),
    Output("elements", "data", allow_duplicate=True),
    Input("group-measures", "value"),
    Input("group-visuals", "value"),
    Input("elements", "data"),
    prevent_initial_call=True,
)
def group_nodes(group_measures, group_visuals, elements):
    # load the data
    _elements = Elements(elements=elements)
    g = Graph.from_elements(_elements)
    new_elements = elements

    if group_measures:
        group_by_measures = group_measures
        node_type = "measure"
        
        new_elements = g.group_by(group_by=group_by_measures, node_type=node_type)
        g = Graph.from_elements(new_elements)

    if group_visuals:
        group_by_visuals = group_visuals
        node_type = "visual"

        new_elements = g.group_by(group_by=group_by_visuals, node_type=node_type)

    new_elements = new_elements.model_dump()["elements"]
    return new_elements, new_elements
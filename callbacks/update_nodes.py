from dash.dependencies import Input, Output, State
from app import app
from components.cytoscape import Elements
from components.graph import Graph
from services.data_loader import load_data


@app.callback(
    Output("cytoscape", "elements"),
    Output("elements", "data"),
    Input("group-measures", "value"),
    Input("group-visuals", "value"),
    Input("location-filter", "value"),
    Input("initial-data", "data"),
    prevent_initial_call=True,
)
def group_nodes(group_measures, group_visuals, selected_locations,elements):
    # load the data
    _elements = Elements(elements=elements)
    g = Graph.from_elements(_elements)

    if selected_locations:
        g.select_related_elements(selected_locations, copy=False)
        

    if group_measures:
        group_by_measures = group_measures
        node_type = "measure"
        if not group_by_measures == "default":
            g.group_by(group_by=group_by_measures, node_type=node_type, copy=False)

    if group_visuals:
        group_by_visuals = group_visuals
        node_type = "visual"
        
        if not group_by_visuals == "default":
            g.group_by(group_by=group_by_visuals, node_type=node_type, copy=False)

    _elements = g.export_elements().model_dump()["elements"]
    return _elements, _elements
from dash.dependencies import Input, Output, State
from app import app
from components.cytoscape import Elements
from components.graph import Graph
from components.nodes_model import Nodes
from services.data_loader import load_data


@app.callback(
    Output("cytoscape", "elements"),
    Output("elements", "data"),
    Input("group-measures", "value"),
    Input("group-visuals", "value"),
    Input("table-filter", "value"),
    Input("initial-data", "data"),
    prevent_initial_call=True,
)
def group_nodes(group_measures, group_visuals, selected_table, model):
    # load the data
    # _elements = Elements(elements=elements)
    # g = Graph.from_elements(_elements)
    _model = Nodes(**model)
    g = Graph.from_model(_model)

    if selected_table:
        g.select_related_elements(
            selected_cluster="table",
            selected_values=selected_table, copy=False)

    if group_measures:
        group_by_measures = group_measures
        type = "measure"
        if not group_by_measures == "default":
            g.group_by(group_by=group_by_measures, type=type, copy=False)

    if group_visuals:
        group_by_visuals = group_visuals
        type = "visual"

        if not group_by_visuals == "default":
            g.group_by(group_by=group_by_visuals, type=type, copy=False)

    _elements = g.export_elements().model_dump()["elements"]
    return _elements, _elements

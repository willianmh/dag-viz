from dash.dependencies import Input, Output, State
from app import app
from assets.stylesheet import default_stylesheet
from components.cytoscape import Elements
from components.graph import Graph


@app.callback(
    Output("cytoscape", "stylesheet"),
    Output("selected-node", "data"),
    Input("cytoscape", "tapNodeData"),
    Input("elements", "data"),
    State("selected-node", "data"),
    prevent_initial_call=True,
)
def highlight_paths(node_data, elements, selected_node):
    if not node_data:
        return default_stylesheet, None

    if selected_node:
        print(f'node: {node_data["id"]} ; selected node: {selected_node}')
        if selected_node == node_data["id"]:
            return default_stylesheet, None

    _elements = Elements(elements=elements)
    g = Graph.from_elements(_elements)
    # _model = Nodes(**model)
    # g = Graph.from_model(_model)

    node_id = node_data["id"]

    # Find all paths that include the selected node
    paths = g.mapping_node_to_path.get(node_id, [])

    # Get the list of nodes and edges to highlight
    nodes_to_highlight = set()
    edges_to_highlight = set()
    for path in paths:
        nodes_to_highlight.update(path)
        edges_in_path = list(zip(path[:-1], path[1:]))
        edges_to_highlight.update(edges_in_path)

    # Start with default stylesheet
    new_stylesheet = default_stylesheet.copy()

    # Highlight nodes
    for node in nodes_to_highlight:
        new_stylesheet.append(
            {
                "selector": f'node[id = "{node}"]',
                "style": {
                    "background-color": "#FFD700",
                    "font-weight": "bold",
                },
            }
        )

    # Highlight edges
    for source, target in edges_to_highlight:
        edge_id = f"{source}->{target}"
        new_stylesheet.append(
            {
                "selector": f'edge[id = "{edge_id}"]',
                "style": {
                    "line-color": "#767676",
                    "width": 1.6,
                    "target-arrow-color": "#767676",
                    "arrow-scale": 1.1,
                },
            }
        )

    return new_stylesheet, node_data["id"]

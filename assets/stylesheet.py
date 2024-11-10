default_stylesheet = [
    # Workspace Group Styling
    {
        "selector": ".group",
        "style": {
            "shape": "roundrectangle",
            "background-opacity": 0.2,
            "background-color": "#f5c87d",
            "label": "data(label)",
            "padding": "20px",
            "text-valign": "top",
            "text-halign": "center",
            "width": "500px",
            "height": "400px",
        },
    },
    # Group Styling for Dataset and Report Nodes
    {
        "selector": ".subgroup",
        "style": {
            "shape": "roundrectangle",
            "background-opacity": 0.3,
            "background-color": "#b0b0b0",
            "label": "data(label)",
            "padding": "10px",
            "text-valign": "top",
            "text-halign": "center",
            "width": "200px",
            "height": "200px",
        },
    },
    {
        "selector": "node",
        "style": {
            "label": "data(label)",
            "content": "data(label)",
            "width": "label",
            "height": "label",
            "color": "#fff",
            "text-valign": "center",
            "text-halign": "center",
            "font-size": "6px",
            "shape": "rectangle",
            "padding": "4px",
        },
    },
    {
        "selector": "edge",
        "style": {
            "line-color": "#9A9A9A",
            "width": 1.4,
            "target-arrow-color": "#9A9A9A",
            "target-arrow-shape": "chevron",
            "curve-style": "bezier",
        },
    },
    {
        "selector": "node[node_type = 'measure']",
        "style": {
            "background-color": "#636EFA",
        },
    },
    {
        "selector": "node[node_type = 'visual']",
        "style": {
            "background-color": "#EF553B",
        },
    },
]

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "24rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

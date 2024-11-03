default_stylesheet = [
    {
        "selector": "node",
        "style": {
            "label": "data(label)",
            "content": "data(label)",
            "width": 'label',
            "height": 'label',
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

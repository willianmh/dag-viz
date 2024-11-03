from dash import Dash
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

from components.graph import Graph
from components.layout import serve_layout

load_figure_template("LUX")

app = Dash(__name__, external_stylesheets=[dbc.themes.LUX])
server = app.server  # For deployment

app.layout = serve_layout()

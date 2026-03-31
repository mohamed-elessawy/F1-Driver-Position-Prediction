from dash import Dash
import dash_bootstrap_components as dbc

app = Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)

app.title = "F1 Head-to-Head Matchup"
server = app.server

from layout import layout
from callbacks import register_callbacks

app.layout = layout
register_callbacks(app)

if __name__ == '__main__':
    app.run(debug=False, port=8050)

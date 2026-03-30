from dash import html, dcc
import dash_bootstrap_components as dbc
import pandas as pd

DATA_PATH = 'Data/'

try:
    drivers_df = pd.read_csv(f'{DATA_PATH}drivers_lookup.csv')
    constructors_df = pd.read_csv(f'{DATA_PATH}constructors_lookup.csv')
    circuits_df = pd.read_csv(f'{DATA_PATH}circuits_lookup.csv')
except FileNotFoundError:
    drivers_df = pd.DataFrame({'driverId': [], 'full_name': []})
    constructors_df = pd.DataFrame({'constructorId': [], 'name': []})
    circuits_df = pd.DataFrame({'circuitId': [], 'name': [], 'country': []})

driver_options = [{'label': r['full_name'], 'value': r['driverId']} for _, r in drivers_df.iterrows()]
constructor_options = [{'label': r['name'], 'value': r['constructorId']} for _, r in constructors_df.iterrows()]
circuit_options = [{'label': f"{r['name']} ({r['country']})", 'value': r['circuitId']} for _, r in circuits_df.iterrows()]

# Sidebar for top drivers
sidebar = html.Div([
    html.H5("Top Drivers", style={'marginBottom': '15px', 'color': '#1a202c'}),
    html.Label("Number of Drivers"),
    dcc.Slider(id='top-n-slider', min=3, max=10, step=1, value=5,
               marks={i: str(i) for i in [3, 5, 7, 10]}),
    html.Div(id='top-drivers-chart', style={'marginTop': '20px'})
], className='sidebar')

# Tab 1: Head-to-Head Stats
tab1_content = dbc.Container([
    dbc.Row([
        dbc.Col([sidebar], md=3),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Select Drivers"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Driver A"),
                            dcc.Dropdown(id='driver-a-dropdown', options=driver_options,
                                        value=driver_options[0]['value'] if driver_options else None)
                        ], md=6),
                        dbc.Col([
                            html.Label("Driver B"),
                            dcc.Dropdown(id='driver-b-dropdown', options=driver_options,
                                        value=driver_options[1]['value'] if len(driver_options) > 1 else None)
                        ], md=6)
                    ])
                ])
            ], className='mb-4'),
            html.Div(id='h2h-charts-container')
        ], md=9)
    ])
], fluid=True)

# Tab 2: Race Predictor
tab2_content = dbc.Container([
    dbc.Card([
        dbc.CardHeader("Race Setup"),
        dbc.CardBody([
            html.Label("Circuit"),
            dcc.Dropdown(id='circuit-dropdown', options=circuit_options,
                        value=circuit_options[0]['value'] if circuit_options else None)
        ])
    ], className='mb-4'),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Driver A"),
                dbc.CardBody([
                    html.Label("Driver"),
                    dcc.Dropdown(id='pred-driver-a', options=driver_options,
                                value=driver_options[0]['value'] if driver_options else None, className='mb-3'),
                    html.Label("Constructor"),
                    dcc.Dropdown(id='constructor-a', options=constructor_options,
                                value=constructor_options[0]['value'] if constructor_options else None, className='mb-3'),
                    html.Label("Grid Position"),
                    dcc.Slider(id='grid-a', min=1, max=20, step=1, value=1,
                              marks={i: str(i) for i in [1, 5, 10, 15, 20]})
                ])
            ])
        ], md=6),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Driver B"),
                dbc.CardBody([
                    html.Label("Driver"),
                    dcc.Dropdown(id='pred-driver-b', options=driver_options,
                                value=driver_options[1]['value'] if len(driver_options) > 1 else None, className='mb-3'),
                    html.Label("Constructor"),
                    dcc.Dropdown(id='constructor-b', options=constructor_options,
                                value=constructor_options[1]['value'] if len(constructor_options) > 1 else None, className='mb-3'),
                    html.Label("Grid Position"),
                    dcc.Slider(id='grid-b', min=1, max=20, step=1, value=2,
                              marks={i: str(i) for i in [1, 5, 10, 15, 20]})
                ])
            ])
        ], md=6)
    ], className='mb-4'),
    html.Div(id='prediction-output', className='prediction-box')
], fluid=True)

layout = html.Div([
    html.Div([html.H1(["F1 ", html.Span("Head-to-Head"), " Matchup"])], className='header'),
    dbc.Tabs([
        dbc.Tab(tab1_content, label="H2H Stats", tab_id='tab-1'),
        dbc.Tab(tab2_content, label="Race Predictor", tab_id='tab-2')
    ], id='tabs', active_tab='tab-1', className='mb-4')
], className='main-container')

from dash import html, dcc
import dash_bootstrap_components as dbc
import pandas as pd
import os

Base_PATH = os.path.dirname(os.path.abspath(__file__))

DATA_PATH = f'{Base_PATH}/data/'
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

# Tab 1: Head-to-Head Stats
tab1_content = dbc.Container([
    dbc.Card([
        dbc.CardHeader("Select Drivers"),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Div("Driver A", className='badge-a'),
                    dcc.Dropdown(
                        id='driver-a-dropdown',
                        options=driver_options,
                        value=driver_options[0]['value'] if driver_options else None,
                        placeholder="Select Driver A..."
                    )
                ], md=5),
                dbc.Col(
                    html.Div(html.Div("VS", className='vs-badge'), className='vs-divider'),
                    md=2
                ),
                dbc.Col([
                    html.Div("Driver B", className='badge-b'),
                    dcc.Dropdown(
                        id='driver-b-dropdown',
                        options=driver_options,
                        value=driver_options[1]['value'] if len(driver_options) > 1 else None,
                        placeholder="Select Driver B..."
                    )
                ], md=5),
            ], align='center')
        ])
    ], className='mb-4'),
    html.Div(id='h2h-charts-container')
], fluid=True)

# Tab 2: Race Predictor
tab2_content = dbc.Container([
    dbc.Card([
        dbc.CardHeader("Circuit Selection"),
        dbc.CardBody([
            dcc.Dropdown(
                id='circuit-dropdown',
                options=circuit_options,
                value=circuit_options[0]['value'] if circuit_options else None,
                placeholder="Select a circuit..."
            )
        ])
    ], className='mb-4'),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Driver A"),
                dbc.CardBody([
                    html.Div("Driver A", className='badge-a'),
                    html.Label("Driver"),
                    dcc.Dropdown(
                        id='pred-driver-a',
                        options=driver_options,
                        value=driver_options[0]['value'] if driver_options else None,
                        placeholder="Select Driver A...",
                        className='mb-3'
                    ),
                    html.Label("Constructor"),
                    dcc.Dropdown(
                        id='constructor-a',
                        options=constructor_options,
                        value=constructor_options[0]['value'] if constructor_options else None,
                        placeholder="Select Constructor...",
                        className='mb-3'
                    ),
                    html.Label("Grid Position"),
                    dcc.Slider(id='grid-a', min=1, max=20, step=1, value=1,
                               marks={i: {'label': str(i), 'style': {'color': '#ffffff'}} for i in [1, 5, 10, 15, 20]})
                ])
            ])
        ], md=6),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Driver B"),
                dbc.CardBody([
                    html.Div("Driver B", className='badge-b'),
                    html.Label("Driver"),
                    dcc.Dropdown(
                        id='pred-driver-b',
                        options=driver_options,
                        value=driver_options[1]['value'] if len(driver_options) > 1 else None,
                        placeholder="Select Driver B...",
                        className='mb-3'
                    ),
                    html.Label("Constructor"),
                    dcc.Dropdown(
                        id='constructor-b',
                        options=constructor_options,
                        value=constructor_options[1]['value'] if len(constructor_options) > 1 else None,
                        placeholder="Select Constructor...",
                        className='mb-3'
                    ),
                    html.Label("Grid Position"),
                    dcc.Slider(id='grid-b', min=1, max=20, step=1, value=2,
                               marks={i: {'label': str(i), 'style': {'color': '#ffffff'}} for i in [1, 5, 10, 15, 20]})
                ])
            ])
        ], md=6)
    ], className='mb-4'),
    html.Div(id='prediction-output', className='prediction-box')
], fluid=True)

# Tab 3: Top Drivers
tab3_content = dbc.Container([
    dbc.Card([
        dbc.CardHeader("Number of Drivers"),
        dbc.CardBody([
            dcc.Slider(id='top-n-slider', min=3, max=10, step=1, value=5,
                       marks={i: {'label': str(i), 'style': {'color': '#ffffff'}} for i in [3, 5, 7, 10]})
        ])
    ], className='mb-4'),
    html.Div(id='top-drivers-chart')
], fluid=True)

layout = html.Div([
    html.Div([
        html.Img(src='/assets/Logo.png', style={'height': '5.5vw', 'objectFit': 'contain', 'marginLeft': '0.5vw'}),
        html.P("DRIVER ANALYTICS & RACE PREDICTION DASHBOARD", className='header-sub')
    ], className='header'),
    dbc.Tabs([
        dbc.Tab(tab1_content, label="H2H Stats",      tab_id='tab-1'),
        dbc.Tab(tab2_content, label="Race Predictor", tab_id='tab-2'),
        dbc.Tab(tab3_content, label="Top Drivers",    tab_id='tab-3'),
    ], id='tabs', active_tab='tab-1', className='mb-4')
], className='main-container')

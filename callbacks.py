from dash import Input, Output, html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import joblib
import os
Base_PATH = os.path.dirname(os.path.abspath(__file__))

DATA_PATH   = f'{Base_PATH}/data/'
MODELS_PATH = f'{Base_PATH}/models/'

# ── Shared dark theme for all figures ──────────────────────────────────────
DARK = dict(
    paper_bgcolor='#171722',
    plot_bgcolor='#13131c',
    font=dict(color='#c0c0d8', family='Inter, system-ui, sans-serif', size=12),
    margin=dict(l=12, r=12, t=44, b=12),
)

RED   = '#e10600'
BLUE  = '#3b82f6'
GREEN = '#22c55e'
AMBER = '#f59e0b'
BAR_PALETTE = [RED, BLUE, GREEN, AMBER, '#8b5cf6', '#ec4899', '#14b8a6', '#f97316', '#06b6d4', '#a3e635']

GRID = dict(gridcolor='rgba(255,255,255,0.05)', zeroline=False)


def _fig_base(**extra):
    layout = {**DARK, **extra}
    return go.Layout(**layout)


def register_callbacks(app):

    # ── Top Drivers bar chart ───────────────────────────────────────────────
    @app.callback(
        Output('top-drivers-chart', 'children'),
        [Input('top-n-slider', 'value')]
    )
    def update_top_drivers(top_n):
        try:
            df         = pd.read_csv(f'{DATA_PATH}f1_cleaned.csv')
            drivers_df = pd.read_csv(f'{DATA_PATH}drivers_lookup.csv')
        except FileNotFoundError:
            return html.Div("Data not found.", className='warning-box')

        wins = df[df['positionOrder'] == 1].groupby('driverId').size().reset_index(name='wins')
        wins = wins.merge(drivers_df[['driverId', 'full_name']], on='driverId')
        wins = wins.nlargest(top_n, 'wins')

        fig = go.Figure(
            go.Bar(
                x=wins['wins'], y=wins['full_name'], orientation='h',
                marker=dict(
                    color=BAR_PALETTE[:len(wins)],
                    line=dict(width=0)
                ),
                text=wins['wins'], textposition='outside',
                textfont=dict(color='#c0c0d8', size=11, family='Inter')
            ),
            layout=_fig_base(
                title=dict(text='Race Wins', font=dict(size=13, color='#8888aa', family='Inter'), x=0),
                height=600,
                xaxis=dict(**GRID, showgrid=True),
                yaxis=dict(**GRID, showgrid=False, categoryorder='total ascending'),
                bargap=0.25
            )
        )
        return dcc.Graph(figure=fig, config={'displayModeBar': False})

    # ── Head-to-Head charts ─────────────────────────────────────────────────
    @app.callback(
        Output('h2h-charts-container', 'children'),
        [Input('driver-a-dropdown', 'value'), Input('driver-b-dropdown', 'value')]
    )
    def update_h2h_charts(driver_a_id, driver_b_id):
        try:
            df         = pd.read_csv(f'{DATA_PATH}f1_cleaned.csv')
            drivers_df = pd.read_csv(f'{DATA_PATH}drivers_lookup.csv')
        except FileNotFoundError:
            return html.Div("Data not found. Run the notebook first.", className='warning-box')

        if not driver_a_id or not driver_b_id:
            return html.Div("Select both drivers to see the comparison.", className='warning-box')

        if driver_a_id == driver_b_id:
            return html.Div("Please select two different drivers to compare.", className='warning-box')

        name_a = drivers_df[drivers_df['driverId'] == driver_a_id]['full_name'].values[0]
        name_b = drivers_df[drivers_df['driverId'] == driver_b_id]['full_name'].values[0]

        data_a = df[df['driverId'] == driver_a_id]
        data_b = df[df['driverId'] == driver_b_id]

        avg_a, avg_b = data_a['positionOrder'].mean(), data_b['positionOrder'].mean()
        pts_a, pts_b = data_a['points'].sum(),        data_b['points'].sum()

        dnf_a    = int(data_a['is_dnf'].sum()) if 'is_dnf' in data_a.columns else 0
        dnf_b    = int(data_b['is_dnf'].sum()) if 'is_dnf' in data_b.columns else 0
        finish_a = len(data_a) - dnf_a
        finish_b = len(data_b) - dnf_b

        bar_layout = dict(height=360, bargap=0.35, xaxis=dict(**GRID, showgrid=False),
                          yaxis=dict(**GRID, showgrid=True))

        fig1 = go.Figure(
            go.Bar(
                x=[name_a, name_b], y=[avg_a, avg_b],
                marker=dict(color=[RED, BLUE], line=dict(width=0)),
                text=[f'{avg_a:.1f}', f'{avg_b:.1f}'], textposition='outside',
                textfont=dict(color='#c0c0d8')
            ),
            layout=_fig_base(
                title=dict(text='Avg Finish Position', font=dict(size=13, color='#8888aa'), x=0),
                yaxis_title='Position (lower = better)',
                **bar_layout
            )
        )

        fig2 = go.Figure(
            go.Bar(
                x=[name_a, name_b], y=[pts_a, pts_b],
                marker=dict(color=[RED, BLUE], line=dict(width=0)),
                text=[f'{pts_a:,.0f}', f'{pts_b:,.0f}'], textposition='outside',
                textfont=dict(color='#c0c0d8')
            ),
            layout=_fig_base(
                title=dict(text='Total Career Points', font=dict(size=13, color='#8888aa'), x=0),
                yaxis_title='Points',
                **bar_layout
            )
        )

        pie_colors = [GREEN, RED]
        fig3 = go.Figure(layout=_fig_base(
            title=dict(text=f'DNF Rate — {name_a}  vs  {name_b}', font=dict(size=13, color='#8888aa'), x=0),
            height=360,
            annotations=[
                dict(text=name_a[:12], x=0.18, y=0.5, showarrow=False, font=dict(color='#f0f0f8', size=12)),
                dict(text=name_b[:12], x=0.82, y=0.5, showarrow=False, font=dict(color='#f0f0f8', size=12))
            ],
            legend=dict(font=dict(color='#8888aa'), bgcolor='rgba(0,0,0,0)')
        ))
        fig3.add_trace(go.Pie(
            labels=['Finished', 'DNF'], values=[finish_a, dnf_a], name=name_a,
            hole=0.55, domain={'x': [0, 0.44]},
            marker_colors=pie_colors,
            textfont=dict(color='#f0f0f8'),
            outsidetextfont=dict(color='#8888aa')
        ))
        fig3.add_trace(go.Pie(
            labels=['Finished', 'DNF'], values=[finish_b, dnf_b], name=name_b,
            hole=0.55, domain={'x': [0.56, 1]},
            marker_colors=pie_colors,
            textfont=dict(color='#f0f0f8'),
            outsidetextfont=dict(color='#8888aa'),
            showlegend=False
        ))

        return html.Div([
            dbc.Row([
                dbc.Col(html.Div(dcc.Graph(figure=fig1, config={'displayModeBar': False}), className='graph-container'), md=6),
                dbc.Col(html.Div(dcc.Graph(figure=fig2, config={'displayModeBar': False}), className='graph-container'), md=6)
            ]),
            dbc.Row([
                dbc.Col(html.Div(dcc.Graph(figure=fig3, config={'displayModeBar': False}), className='graph-container'), md=12)
            ])
        ])

    # ── Race Predictor ──────────────────────────────────────────────────────
    @app.callback(
        Output('prediction-output', 'children'),
        [Input('circuit-dropdown', 'value'),
         Input('pred-driver-a', 'value'), Input('pred-driver-b', 'value'),
         Input('constructor-a', 'value'),  Input('constructor-b', 'value'),
         Input('grid-a', 'value'),         Input('grid-b', 'value')]
    )
    def predict_race(circuit_id, driver_a_id, driver_b_id, constructor_a, constructor_b, grid_a, grid_b):
        try:
            clf        = joblib.load(f'{MODELS_PATH}rf_h2h.pkl')
            meta       = joblib.load(f'{MODELS_PATH}model_meta.pkl')
            drivers_df = pd.read_csv(f'{DATA_PATH}drivers_lookup.csv')
        except FileNotFoundError:
            return html.Div("Model not found. Run the notebook first.", className='warning-box')

        if not all([circuit_id, driver_a_id, driver_b_id, constructor_a, constructor_b]):
            return html.Div("Please fill in all fields to get a prediction.", className='warning-box')

        if driver_a_id == driver_b_id:
            return html.Div("Select two different drivers.", className='warning-box')

        if grid_a == grid_b:
            return html.Div("Grid positions must be unique.", className='warning-box')

        name_a = drivers_df[drivers_df['driverId'] == driver_a_id]['full_name'].values[0]
        name_b = drivers_df[drivers_df['driverId'] == driver_b_id]['full_name'].values[0]

        driver_stats         = meta['driver_stats']
        circuit_driver_stats = meta['circuit_driver_stats']
        constructor_stats    = meta['constructor_stats']
        global_avg_pos       = meta['global_avg_pos']
        global_avg_pts       = meta['global_avg_pts']

        def _avg_pos(driver_id):
            row = driver_stats[driver_stats['driverId'] == driver_id]
            return float(row['avg_pos'].values[0]) if len(row) else global_avg_pos

        def _circuit_avg(driver_id, cid):
            row = circuit_driver_stats[
                (circuit_driver_stats['driverId'] == driver_id) &
                (circuit_driver_stats['circuitId'] == cid)
            ]
            return float(row['circuit_avg_pos'].values[0]) if len(row) else _avg_pos(driver_id)

        def _constructor_pts(constructor_id):
            row = constructor_stats[constructor_stats['constructorId'] == constructor_id]
            return float(row['avg_pts'].values[0]) if len(row) else global_avg_pts

        features = pd.DataFrame([[
            grid_a, grid_b,
            _avg_pos(driver_a_id),       _avg_pos(driver_b_id),
            _circuit_avg(driver_a_id, circuit_id), _circuit_avg(driver_b_id, circuit_id),
            _constructor_pts(constructor_a), _constructor_pts(constructor_b)
        ]], columns=meta['feature_columns'])

        prob_a_wins = clf.predict_proba(features)[0][1]

        if prob_a_wins >= 0.5:
            winner, win_color, confidence = name_a, RED,  prob_a_wins
        else:
            winner, win_color, confidence = name_b, BLUE, 1.0 - prob_a_wins

        return html.Div([
            html.P("RACE PREDICTION RESULTS",
                   style={'color': '#505068', 'fontSize': '0.7rem', 'fontWeight': '700',
                          'letterSpacing': '2px', 'marginBottom': '20px'}),
            dbc.Row([
                dbc.Col([
                    html.Div("Driver A", className='badge-a'),
                    html.P(html.Strong(name_a),
                           style={'fontSize': '1.1rem', 'color': '#c0c0d8', 'marginBottom': '6px',
                                  'textAlign': 'center'})
                ], md=5, style={'textAlign': 'center'}),
                dbc.Col(
                    html.Div(html.Div("VS", className='vs-badge'), className='vs-divider'),
                    md=2
                ),
                dbc.Col([
                    html.Div("Driver B", className='badge-b'),
                    html.P(html.Strong(name_b),
                           style={'fontSize': '1.1rem', 'color': '#c0c0d8', 'marginBottom': '6px',
                                  'textAlign': 'center'})
                ], md=5, style={'textAlign': 'center'}),
            ], align='center', className='mb-4'),
            html.Hr(),
            html.Div([
                html.P("PREDICTED WINNER",
                       style={'color': '#505068', 'fontSize': '0.68rem', 'fontWeight': '700',
                              'letterSpacing': '2px', 'marginBottom': '8px'}),
                html.H2(winner, style={'color': win_color, 'fontWeight': '900',
                                       'fontSize': '2.2rem', 'letterSpacing': '-0.5px',
                                       'textShadow': f'0 0 30px {win_color}88'}),
                html.P(f"Model confidence: {confidence:.0%}",
                       style={'color': '#8888aa', 'fontSize': '0.85rem', 'marginTop': '8px'})
            ], style={'textAlign': 'center', 'padding': '10px 0'})
        ])

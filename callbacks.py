from dash import Input, Output, html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import joblib

DATA_PATH = 'Data/'

def register_callbacks(app):
    
    @app.callback(
        Output('top-drivers-chart', 'children'),
        [Input('top-n-slider', 'value')]
    )
    def update_top_drivers(top_n):
        try:
            df = pd.read_csv(f'{DATA_PATH}f1_cleaned.csv')
            drivers_df = pd.read_csv(f'{DATA_PATH}drivers_lookup.csv')
        except FileNotFoundError:
            return html.Div("Data not found.", className='warning-box')
        
        # Count wins (positionOrder == 1) per driver
        wins = df[df['positionOrder'] == 1].groupby('driverId').size().reset_index(name='wins')
        wins = wins.merge(drivers_df[['driverId', 'full_name']], on='driverId')
        wins = wins.nlargest(top_n, 'wins')
        
        colors = ['#c41e3a', '#2b6cb0', '#38a169', '#d69e2e', '#805ad5', '#dd6b20', '#319795', '#e53e3e', '#3182ce', '#48bb78']
        
        fig = go.Figure(go.Bar(
            x=wins['wins'], y=wins['full_name'], orientation='h',
            marker_color=colors[:len(wins)],
            text=wins['wins'], textposition='outside'
        ))
        fig.update_layout(
            title='Race Wins', height=300,
            paper_bgcolor='#fff', plot_bgcolor='#f7fafc',
            font=dict(color='#2d3748'), margin=dict(l=10, r=10, t=40, b=10),
            yaxis=dict(categoryorder='total ascending')
        )
        return dcc.Graph(figure=fig, config={'displayModeBar': False})
    
    @app.callback(
        Output('h2h-charts-container', 'children'),
        [Input('driver-a-dropdown', 'value'), Input('driver-b-dropdown', 'value')]
    )
    def update_h2h_charts(driver_a_id, driver_b_id):
        try:
            df = pd.read_csv(f'{DATA_PATH}f1_cleaned.csv')
            drivers_df = pd.read_csv(f'{DATA_PATH}drivers_lookup.csv')
        except FileNotFoundError:
            return html.Div("Data not found. Run the notebook first.", className='warning-box')
        
        if not driver_a_id or not driver_b_id:
            return html.Div("Select both drivers.", className='warning-box')
        
        if driver_a_id == driver_b_id:
            return html.Div("Please select two different drivers to compare.", className='warning-box')
        
        name_a = drivers_df[drivers_df['driverId'] == driver_a_id]['full_name'].values[0]
        name_b = drivers_df[drivers_df['driverId'] == driver_b_id]['full_name'].values[0]
        
        data_a = df[df['driverId'] == driver_a_id]
        data_b = df[df['driverId'] == driver_b_id]
        
        avg_a, avg_b = data_a['positionOrder'].mean(), data_b['positionOrder'].mean()
        pts_a, pts_b = data_a['points'].sum(), data_b['points'].sum()
        
        dnf_a = (data_a['positionOrder'] > 20).sum()
        dnf_b = (data_b['positionOrder'] > 20).sum()
        finish_a, finish_b = len(data_a) - dnf_a, len(data_b) - dnf_b
        
        layout_common = dict(paper_bgcolor='#fff', plot_bgcolor='#f7fafc', 
                            font=dict(color='#2d3748'), height=350, margin=dict(t=50, b=40))
        colors = ['#c41e3a', '#2b6cb0']
        
        fig1 = go.Figure(go.Bar(x=[name_a, name_b], y=[avg_a, avg_b], marker_color=colors,
                                text=[f'{avg_a:.1f}', f'{avg_b:.1f}'], textposition='outside'))
        fig1.update_layout(title='Average Finish Position', yaxis_title='Position (lower=better)', **layout_common)
        
        fig2 = go.Figure(go.Bar(x=[name_a, name_b], y=[pts_a, pts_b], marker_color=colors,
                                text=[f'{pts_a:.0f}', f'{pts_b:.0f}'], textposition='outside'))
        fig2.update_layout(title='Total Career Points', yaxis_title='Points', **layout_common)
        
        fig3 = go.Figure()
        fig3.add_trace(go.Pie(labels=['Finished', 'DNF'], values=[finish_a, dnf_a], name=name_a,
                             hole=0.5, domain={'x': [0, 0.45]}, marker_colors=['#38a169', '#c41e3a']))
        fig3.add_trace(go.Pie(labels=['Finished', 'DNF'], values=[finish_b, dnf_b], name=name_b,
                             hole=0.5, domain={'x': [0.55, 1]}, marker_colors=['#38a169', '#2b6cb0']))
        fig3.update_layout(title=f'DNF Rate: {name_a} vs {name_b}', 
                          annotations=[dict(text=name_a[:10], x=0.18, y=0.5, showarrow=False),
                                      dict(text=name_b[:10], x=0.82, y=0.5, showarrow=False)],
                          **layout_common)
        
        return html.Div([
            dbc.Row([
                dbc.Col(html.Div(dcc.Graph(figure=fig1), className='graph-container'), md=6),
                dbc.Col(html.Div(dcc.Graph(figure=fig2), className='graph-container'), md=6)
            ]),
            dbc.Row([dbc.Col(html.Div(dcc.Graph(figure=fig3), className='graph-container'), md=12)])
        ])
    
    @app.callback(
        Output('prediction-output', 'children'),
        [Input('circuit-dropdown', 'value'), Input('pred-driver-a', 'value'), Input('pred-driver-b', 'value'),
         Input('constructor-a', 'value'), Input('constructor-b', 'value'),
         Input('grid-a', 'value'), Input('grid-b', 'value')]
    )
    def predict_race(circuit_id, driver_a_id, driver_b_id, constructor_a, constructor_b, grid_a, grid_b):
        try:
            clf = joblib.load(f'{DATA_PATH}rf_classifier_h2h.pkl')
            drivers_df = pd.read_csv(f'{DATA_PATH}drivers_lookup.csv')
        except FileNotFoundError:
            return html.Div("Model not found. Run the notebook first.", className='warning-box')
        
        if not all([circuit_id, driver_a_id, driver_b_id, constructor_a, constructor_b]):
            return html.Div("Please select all inputs.", className='warning-box')
        
        if driver_a_id == driver_b_id:
            return html.Div("Same driver cannot compete with himself. Select different drivers.", className='warning-box')
        
        if grid_a == grid_b:
            return html.Div("Grid positions must be unique for each driver.", className='warning-box')
        
        name_a = drivers_df[drivers_df['driverId'] == driver_a_id]['full_name'].values[0]
        name_b = drivers_df[drivers_df['driverId'] == driver_b_id]['full_name'].values[0]
        
        pit_default = 25000
        features_a = [[driver_a_id, constructor_a, circuit_id, grid_a, grid_a, pit_default]]
        features_b = [[driver_b_id, constructor_b, circuit_id, grid_b, grid_b, pit_default]]
        
        pred_a, pred_b = clf.predict(features_a)[0], clf.predict(features_b)[0]
        
        if pred_a < pred_b:
            winner, color = name_a, '#c41e3a'
        elif pred_b < pred_a:
            winner, color = name_b, '#2b6cb0'
        else:
            winner, color = "TIE", '#d69e2e'
        
        return html.Div([
            html.H4("Race Prediction Results", className='mb-3', style={'color': '#1a202c'}),
            html.P([html.Strong(f"{name_a}: "), f"P{pred_a}"], style={'fontSize': '1.2rem', 'color': '#2d3748'}),
            html.P([html.Strong(f"{name_b}: "), f"P{pred_b}"], style={'fontSize': '1.2rem', 'color': '#2d3748'}),
            html.Hr(),
            html.Div([
                html.P("PREDICTED WINNER", style={'color': '#718096', 'marginBottom': '5px'}),
                html.H3(winner, style={'color': color, 'fontWeight': '700'})
            ], style={'textAlign': 'center'})
        ])

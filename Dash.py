import dash
from dash import dcc, html, Input, Output, dash_table, callback, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import requests
import dash_bootstrap_components as dbc
from flask import request, jsonify
from datetime import datetime

# Initialize the Dash app with Bootstrap
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
server = app.server

# Global variable to store mobile data
mobile_data_store = {
    'sensor_data': [],
    'last_update': None
}

# API endpoint to receive mobile data
@server.route('/api/mobile-data', methods=['POST'])
def receive_mobile_data():
    global mobile_data_store
    try:
        data = request.json
        print("Received mobile data:", data)
        
        # Add timestamp and store data
        data['timestamp'] = datetime.now().isoformat()
        mobile_data_store['sensor_data'].append(data)
        mobile_data_store['last_update'] = datetime.now()
        
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Backend API URL (replace with your actual API endpoint)
API_URL = "http://your-backend-api.com/data"

# Function to fetch data from the backend
def fetch_data():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        data = response.json()

        # Parse the data into DataFrames
        device_data = data.get("device_data", [])
        system_data = data.get("system_data", [])
        pi_data = data.get("pi_data", [])
        time_data = data.get("time_data", [])

        return (
            pd.DataFrame(device_data),
            pd.DataFrame(system_data),
            pd.DataFrame(pi_data),
            pd.DataFrame(time_data),
        )
    except Exception as e:
        print(f"Error fetching data: {e}")
        return (
            pd.DataFrame({"Device": [], "Power Usage": []}),
            pd.DataFrame({"Category": [], "Value": []}),
            pd.DataFrame({"Category": [], "Value": []}),
            pd.DataFrame({"Time": [], "Detection Time": []}),
        )

# Custom styles
CARD_STYLE = {
    'border': '1px solid #444',
    'borderRadius': '5px',
    'padding': '10px',
    'marginBottom': '15px',
    'height': '100%'
}

GRAPH_CONFIG = {
    'displayModeBar': False,
    'responsive': True
}

# Layout for the dashboard
app.layout = dbc.Container(fluid=True, children=[
    # Header Section
    dbc.Row([
        dbc.Col(html.H1("Smart Visual Hat Monitoring Dashboard", 
                       className="text-center my-4"),
                width=12)
    ]),
    
    # Interval component for data refresh
    dcc.Interval(id='interval-component', interval=1000, n_intervals=0),
    dcc.Store(id='mobile-data-store'),
    
    # Mobile Data Display Section
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Mobile Sensor Data", className="text-center"),
                dbc.CardBody([
                    html.Div(id='mobile-data-display'),
                    dash_table.DataTable(
                        id='mobile-data-table',
                        columns=[
                            {'name': 'Sensor', 'id': 'sensor'},
                            {'name': 'Value', 'id': 'value'},
                            {'name': 'Timestamp', 'id': 'timestamp'}
                        ],
                        style_table={
                            'overflowX': 'auto',
                            'backgroundColor': 'transparent'
                        },
                        style_cell={
                            'textAlign': 'left',
                            'padding': '10px',
                            'backgroundColor': 'transparent',
                            'color': 'white',
                            'border': 'none'
                        },
                        style_header={
                            'backgroundColor': '#2c3e50',
                            'color': 'white',
                            'fontWeight': 'bold'
                        }
                    )
                ])
            ], style=CARD_STYLE)
        ], width=12)
    ], className="mb-4"),
    
    # First row: Device Distribution and KPI Cards
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id='device-distribution', config=GRAPH_CONFIG)
                ])
            ], style=CARD_STYLE)
        ], md=6, xs=12),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H3("System KPIs", className="text-center mb-3"),
                    html.Div(id='kpi-cards')
                ])
            ], style=CARD_STYLE)
        ], md=6, xs=12)
    ], className="mb-4"),
    
    # Rest of your existing layout...
    # (Keep all your existing rows for device distribution, power management, etc.)
    
    # API Info Section
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Mobile Integration API", className="text-center"),
                dbc.CardBody([
                    html.P("Send mobile data to:", className="mb-1"),
                    html.P("POST https://your-dash-app-url/api/mobile-data", className="font-monospace"),
                    html.P("JSON format: {'sensor': 'temperature', 'value': 25.4}", className="mt-2"),
                    html.Div(id='api-status', className="mt-2")
                ])
            ], style=CARD_STYLE)
        ], width=12)
    ], className="mb-4")
])

# Callback to update mobile data display
@callback(
    [Output('mobile-data-display', 'children'),
     Output('mobile-data-table', 'data')],
    [Input('interval-component', 'n_intervals')]
)
def update_mobile_data(n):
    global mobile_data_store
    
    if not mobile_data_store['sensor_data']:
        return "No mobile data received yet", []
    
    # Prepare data for display
    latest_data = mobile_data_store['sensor_data'][-1]
    table_data = [{
        'sensor': k,
        'value': v,
        'timestamp': latest_data.get('timestamp', 'N/A')
    } for k, v in latest_data.items() if k != 'timestamp']
    
    last_update = mobile_data_store['last_update'].strftime("%Y-%m-%d %H:%M:%S") if mobile_data_store['last_update'] else "Never"
    
    display_content = [
        html.H4(f"Last Update: {last_update}", className="mb-3"),
        html.P(f"Latest Values:", className="mb-1"),
        html.Ul([html.Li(f"{k}: {v}") for k, v in latest_data.items() if k != 'timestamp'])
    ]
    
    return display_content, table_data

# Your existing update_data callback remains the same
@callback(
    [Output('device-distribution', 'figure'),
     Output('power-management', 'figure'),
     Output('power-management-table', 'data'),
     Output('system-performance', 'figure'),
     Output('raspberry-pi', 'figure'),
     Output('temperature-level', 'figure'),
     Output('object-detection-time', 'figure'),
     Output('kpi-cards', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_data(n_intervals):
    # Your existing update_data implementation
    pass

# Running the server
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8050)
import dash
from dash import dcc, html, Input, Output, dash_table, callback
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import requests
import dash_bootstrap_components as dbc
from datetime import datetime
import os

# Initialize the Dash app with Bootstrap
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
server = app.server

# =============================================
# Configuration (Update these for your API)
# =============================================

# API Settings (replace with your actual endpoint)
API_URL = os.getenv('API_URL', 'http://your-visual-hat-api.com/data')  # From environment variables or default
API_KEY = os.getenv('API_KEY', '')  # For authenticated APIs

# Expected data categories (keep these to validate API response)
DEVICE_NAMES = ["Camera", "Processor", "Sensors", "WiFi Module"]
SYSTEM_CATEGORIES = ["CPU", "Memory", "Storage", "Network"]
PI_CATEGORIES = ["CPU Temp", "GPU Temp", "Memory Usage", "Disk Usage"]

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

SECTION_HEADER_STYLE = {
    'color': '#ffffff',
    'borderBottom': '2px solid #444',
    'paddingBottom': '10px',
    'marginTop': '20px'
}

# =============================================
# Dashboard Layout
# =============================================

app.layout = dbc.Container(fluid=True, children=[
    # Header Section
    dbc.Row([
        dbc.Col(html.H1("Smart Visual Hat Monitoring Dashboard", 
                      className="text-center my-4"),
                width=12)
    ]),
    
    # Interval component for data refresh
    dcc.Interval(id='interval-component', interval=1000, n_intervals=0),
    
    # Data status indicator (hidden by default)
    html.Div(id='data-status', style={'display': 'none'}),
    
    # ---- Device Monitoring Section ----
    dbc.Row([
        dbc.Col(html.H2("Device Monitoring", style=SECTION_HEADER_STYLE), width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Device Power Distribution", className="h5"),
                dbc.CardBody([
                    dcc.Graph(id='device-distribution', config=GRAPH_CONFIG)
                ])
            ], style=CARD_STYLE)
        ], md=6, xs=12),
        
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("System KPIs", className="h5"),
                dbc.CardBody([
                    html.Div(id='kpi-cards')
                ])
            ], style=CARD_STYLE)
        ], md=6, xs=12)
    ], className="mb-4"),
    
    # ---- Power Management Section ----
    dbc.Row([
        dbc.Col(html.H2("Power Management", style=SECTION_HEADER_STYLE), width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Power Usage by Category", className="h5"),
                dbc.CardBody([
                    dcc.Graph(id='power-management', config=GRAPH_CONFIG)
                ])
            ], style=CARD_STYLE)
        ], md=8, xs=12),
        
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Device Power Details", className="h5"),
                dbc.CardBody([
                    dash_table.DataTable(
                        id='power-management-table',
                        columns=[{'name': 'Device', 'id': 'Device'}, 
                                {'name': 'Power Usage', 'id': 'Power Usage'}],
                        style_table={
                            'overflowX': 'auto',
                            'height': '300px',
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
        ], md=4, xs=12)
    ], className="mb-4"),
    
    # ---- System Performance Section ----
    dbc.Row([
        dbc.Col(html.H2("System Performance", style=SECTION_HEADER_STYLE), width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("System Metrics", className="h5"),
                dbc.CardBody([
                    dcc.Graph(id='system-performance', config=GRAPH_CONFIG)
                ])
            ], style=CARD_STYLE)
        ], md=6, xs=12),
        
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Raspberry Pi Health", className="h5"),
                dbc.CardBody([
                    dcc.Graph(id='raspberry-pi', config=GRAPH_CONFIG)
                ])
            ], style=CARD_STYLE)
        ], md=6, xs=12)
    ], className="mb-4"),
    
    # ---- Environmental Monitoring Section ----
    dbc.Row([
        dbc.Col(html.H2("Environmental Monitoring", style=SECTION_HEADER_STYLE), width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Temperature Levels", className="h5"),
                dbc.CardBody([
                    dcc.Graph(id='temperature-level', config=GRAPH_CONFIG)
                ])
            ], style=CARD_STYLE)
        ], md=6, xs=12),
        
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Object Detection Times", className="h5"),
                dbc.CardBody([
                    dcc.Graph(id='object-detection-time', config=GRAPH_CONFIG)
                ])
            ], style=CARD_STYLE)
        ], md=6, xs=12)
    ], className="mb-4"),
    
    # ---- Control Panel Section ----
    dbc.Row([
        dbc.Col(html.H2("Control Panel", style=SECTION_HEADER_STYLE), width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dbc.ButtonGroup([
                dbc.Button("Temperature Stats", id='temp-stats-btn', color="primary", className="mx-1"),
                dbc.Button("Network Stability", id='network-stability-btn', color="primary", className="mx-1"),
                dbc.Button("Device Config", id='device-config-btn', color="primary", className="mx-1"),
                dbc.Button("Overall Performance", id='overall-performance-btn', color="primary", className="mx-1"),
            ], className="d-flex flex-wrap justify-content-center")
        ], width=12)
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            dbc.Button("Download Report", id='download-report-btn', color="success", className="d-block mx-auto")
        ], width=12)
    ], className="mb-4"),
    
    # Response area
    dbc.Row([
        dbc.Col([
            html.Div(id='button-response', className="text-center py-3")
        ], width=12)
    ]),
    
    # Download component
    dcc.Download(id='download-report')
])

# =============================================
# API Service Layer
# =============================================

class DataService:
    @staticmethod
    def fetch_live_data():
        """Fetches real-time data from API with error handling"""
        headers = {'Authorization': f'Bearer {API_KEY}'} if API_KEY else {}
        
        try:
            response = requests.get(API_URL, headers=headers, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"API Connection Failed: {str(e)}")

# =============================================
# Callbacks with Pure API Integration
# =============================================

@app.callback(
    [Output('device-distribution', 'figure'),
     Output('power-management', 'figure'),
     Output('power-management-table', 'data'),
     Output('system-performance', 'figure'),
     Output('raspberry-pi', 'figure'),
     Output('temperature-level', 'figure'),
     Output('object-detection-time', 'figure'),
     Output('kpi-cards', 'children'),
     Output('data-status', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_dashboard(n):
    try:
        # Get FRESH data from API every callback
        api_data = DataService.fetch_live_data()
        
        # Validate and transform API response
        device_df = pd.DataFrame(api_data['device_data']).rename(
            columns={'name': 'Device', 'power': 'Power Usage'})
        
        system_df = pd.DataFrame({
            'Category': SYSTEM_CATEGORIES,
            'Value': [
                float(api_data['system_data']['cpu_usage']),
                float(api_data['system_data']['memory_usage']),
                float(api_data['system_data']['storage_usage']),
                float(api_data['system_data']['network_usage'])
            ]
        })
        
        pi_df = pd.DataFrame({
            'Category': PI_CATEGORIES,
            'Value': [
                float(api_data['pi_data']['cpu_temp']),
                float(api_data['pi_data']['gpu_temp']),
                float(api_data['pi_data']['memory_usage']),
                float(api_data['pi_data']['disk_usage'])
            ]
        })
        
        time_df = pd.DataFrame(api_data['time_data'])
        time_df['Time'] = pd.to_datetime(time_df['timestamp'])
        time_df['Detection Time'] = time_df['detection_time'].astype(float)
        time_df['Temperature'] = time_df['temperature'].astype(float)
        
        status = "Live data"
        
    except Exception as e:
        # Minimal fallback - empty but valid structures
        device_df = pd.DataFrame(columns=['Device', 'Power Usage'])
        system_df = pd.DataFrame(columns=['Category', 'Value'])
        pi_df = pd.DataFrame(columns=['Category', 'Value'])
        time_df = pd.DataFrame(columns=['Time', 'Detection Time', 'Temperature'])
        status = f"Error: {str(e)}"

    # Generate visualizations
    device_fig = px.bar(
        device_df,
        x="Device",
        y="Power Usage",
        color="Device",
        color_discrete_sequence=px.colors.qualitative.Pastel
    ).update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        showlegend=False
    )

    power_fig = px.bar(
        system_df,
        x="Value",
        y="Category",
        orientation='h',
        color="Category",
        color_discrete_sequence=px.colors.qualitative.Set3
    ).update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        showlegend=False
    )

    raspberry_pi_fig = go.Figure(go.Pie(
        labels=pi_df['Category'],
        values=pi_df['Value'],
        hole=0.4,
        marker_colors=px.colors.sequential.Viridis,
        textinfo='percent+label'
    )).update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        showlegend=False
    )

    system_performance_fig = go.Figure(go.Pie(
        labels=system_df['Category'],
        values=system_df['Value'],
        hole=0.4,
        marker_colors=px.colors.sequential.Plasma,
        textinfo='percent+label'
    )).update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        showlegend=False
    )

    temp_fig = px.line(
        time_df,
        x="Time",
        y="Temperature",
        color_discrete_sequence=['#00CC96']
    ).update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white'
    )

    detection_fig = px.line(
        time_df,
        x="Time",
        y="Detection Time",
        color_discrete_sequence=['#EF553B']
    ).update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white'
    )

    # KPI Cards
    kpi_cards = dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4("CPU Load", className="card-title"),
                html.H2(f"{system_df.loc[system_df['Category'] == 'CPU', 'Value'].values[0]:.1f}%", 
                       className="card-text")
            ])
        ], color="primary", inverse=True), md=3, sm=6, xs=6, className="mb-3"),
        
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4("RAM Usage", className="card-title"),
                html.H2(f"{system_df.loc[system_df['Category'] == 'Memory', 'Value'].values[0]:.1f}%", 
                       className="card-text")
            ])
        ], color="success", inverse=True), md=3, sm=6, xs=6, className="mb-3"),
        
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4("Power Usage", className="card-title"),
                html.H2(f"{device_df['Power Usage'].sum():.1f}W", 
                       className="card-text")
            ])
        ], color="warning", inverse=True), md=3, sm=6, xs=6, className="mb-3"),
        
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4("Detections", className="card-title"),
                html.H2(f"{len(time_df)}", 
                       className="card-text")
            ])
        ], color="danger", inverse=True), md=3, sm=6, xs=6, className="mb-3")
    ])

    return (
        device_fig, power_fig, device_df.to_dict('records'),
        system_performance_fig, raspberry_pi_fig,
        temp_fig, detection_fig, kpi_cards,
        status
    )

# =============================================
# Run the App
# =============================================

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8050)
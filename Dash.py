import dash
from dash import dcc, html, Input, Output, dash_table, callback
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import requests
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta
import numpy as np

# Initialize the Dash app with Bootstrap
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
server = app.server

# =============================================
# Data Configuration
# =============================================

# Configure your API endpoint here
API_URL = "http://your-api-endpoint.com/data"  # Replace with your actual API endpoint

# Define your device names and expected data structure
DEVICE_NAMES = ["Camera", "Processor", "Sensors", "WiFi Module"]
SYSTEM_CATEGORIES = ["CPU", "Memory", "Storage", "Network"]
PI_CATEGORIES = ["CPU Temp", "GPU Temp", "Memory Usage", "Disk Usage"]

# =============================================
# Styles and Layout
# =============================================

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
# Callbacks
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
def update_data(n_intervals):
    try:
        # Fetch data from API
        response = requests.get(API_URL, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        # Process device data
        device_data = data.get('device_data', [])
        device_df = pd.DataFrame([{
            'Device': d.get('name', 'Unknown'),
            'Power Usage': float(d.get('power', 0))
        } for d in device_data])
        
        # Process system data
        system_data = data.get('system_data', {})
        system_df = pd.DataFrame({
            'Category': SYSTEM_CATEGORIES,
            'Value': [
                float(system_data.get('cpu_usage', 0)),
                float(system_data.get('memory_usage', 0)),
                float(system_data.get('storage_usage', 0)),
                float(system_data.get('network_usage', 0))
            ]
        })
        
        # Process Raspberry Pi data
        pi_data = data.get('pi_data', {})
        pi_df = pd.DataFrame({
            'Category': PI_CATEGORIES,
            'Value': [
                float(pi_data.get('cpu_temp', 0)),
                float(pi_data.get('gpu_temp', 0)),
                float(pi_data.get('memory_usage', 0)),
                float(pi_data.get('disk_usage', 0))
            ]
        })
        
        # Process time series data
        time_data = data.get('time_data', [])
        time_df = pd.DataFrame([{
            'Time': datetime.fromisoformat(t.get('timestamp')),
            'Detection Time': float(t.get('detection_time', 0)),
            'Temperature': float(t.get('temperature', 0))
        } for t in time_data])
        
        data_status = "success"
        
    except Exception as e:
        # Return empty dataframes if API fails
        device_df = pd.DataFrame({'Device': DEVICE_NAMES, 'Power Usage': [0]*len(DEVICE_NAMES)})
        system_df = pd.DataFrame({'Category': SYSTEM_CATEGORIES, 'Value': [0]*len(SYSTEM_CATEGORIES)})
        pi_df = pd.DataFrame({'Category': PI_CATEGORIES, 'Value': [0]*len(PI_CATEGORIES)})
        time_df = pd.DataFrame({'Time': [datetime.now()], 'Detection Time': [0], 'Temperature': [0]})
        data_status = f"error: {str(e)}"

    # Device Distribution Chart
    device_fig = px.bar(
        device_df, 
        x="Device", 
        y="Power Usage", 
        title="",
        color="Device",
        color_discrete_sequence=px.colors.qualitative.Pastel
    ).update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        showlegend=False
    )

    # Power Management Chart
    power_fig = px.bar(
        system_df, 
        x="Value", 
        y="Category", 
        orientation='h', 
        title="",
        color="Category",
        color_discrete_sequence=px.colors.qualitative.Set3
    ).update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        showlegend=False
    )

    # Raspberry Pi Performance
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

    # System Performance
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

    # Temperature Levels
    temp_fig = px.line(
        time_df, 
        x="Time", 
        y="Temperature", 
        title="",
        color_discrete_sequence=['#00CC96']
    ).update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white'
    )

    # Object Detection Time
    detection_fig = px.line(
        time_df, 
        x="Time", 
        y="Detection Time", 
        title="",
        color_discrete_sequence=['#EF553B']
    ).update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white'
    )

    # KPI Cards
    kpi_cards = dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("CPU Load", className="card-title"),
                    html.H2(f"{system_df.loc[system_df['Category'] == 'CPU', 'Value'].values[0]:.1f}%", 
                           className="card-text")
                ])
            ], color="primary", inverse=True)
        ], md=3, sm=6, xs=6, className="mb-3"),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("RAM Usage", className="card-title"),
                    html.H2(f"{system_df.loc[system_df['Category'] == 'Memory', 'Value'].values[0]:.1f}%", 
                           className="card-text")
                ])
            ], color="success", inverse=True)
        ], md=3, sm=6, xs=6, className="mb-3"),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Power Usage", className="card-title"),
                    html.H2(f"{device_df['Power Usage'].sum():.1f}W", 
                           className="card-text")
                ])
            ], color="warning", inverse=True)
        ], md=3, sm=6, xs=6, className="mb-3"),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Detections", className="card-title"),
                    html.H2(f"{len(time_df)}", 
                           className="card-text")
                ])
            ], color="danger", inverse=True)
        ], md=3, sm=6, xs=6, className="mb-3")
    ])

    return (
        device_fig, power_fig, device_df.to_dict('records'),
        system_performance_fig, raspberry_pi_fig,
        temp_fig, detection_fig, kpi_cards,
        data_status
    )

# =============================================
# Run the App
# =============================================

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8050)
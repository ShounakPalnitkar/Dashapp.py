import dash
from dash import dcc, html, Input, Output, dash_table, callback, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta
import numpy as np
import base64
import io

# Initialize the Dash app with Bootstrap
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
server = app.server

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
    
    # File Upload Section
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Upload Data File", className="h5"),
                dbc.CardBody([
                    dcc.Upload(
                        id='upload-data',
                        children=html.Div([
                            'Drag and Drop or ',
                            html.A('Select a File')
                        ]),
                        style={
                            'width': '100%',
                            'height': '60px',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center',
                            'margin': '10px'
                        },
                        multiple=False
                    ),
                    html.Div(id='output-data-upload'),
                ])
            ], style=CARD_STYLE)
        ], width=12)
    ]),
    
    # Interval component for data refresh
    dcc.Interval(id='interval-component', interval=1000*60, n_intervals=0),  # Update every minute
    
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
    dcc.Download(id='download-report'),
    
    # Store for the uploaded data
    dcc.Store(id='stored-data')
])

# =============================================
# Callbacks
# =============================================

def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an Excel file
            df = pd.read_excel(io.BytesIO(decoded))
        else:
            return None, "Unsupported file format"
            
        # Process the data to match expected format
        system_stats = df[df['event_type'] == 'system_stats']
        detections = df[df['event_type'] == 'detection']
        
        # Create device data (mock since not in original data)
        devices = ["Camera", "Processor", "Sensors", "WiFi Module"]
        device_df = pd.DataFrame({
            "Device": devices,
            "Power Usage": [2.5, 3.8, 1.2, 1.5]  # Mock values
        })
        
        # Create system performance data
        system_df = pd.DataFrame({
            "Category": ["CPU", "Memory", "Storage", "Network"],
            "Value": [
                system_stats['CPU'].mean(),
                system_stats['MEM'].mean(),
                78,  # Mock storage value
                12   # Mock network value
            ]
        })
        
        # Raspberry Pi data
        pi_df = pd.DataFrame({
            "Category": ["CPU Temp", "GPU Temp", "Memory Usage", "Disk Usage"],
            "Value": [
                float(system_stats['TEMP'].str.replace("'C", "").mean()),
                55,  # Mock GPU temp
                system_stats['MEM'].mean(),
                30   # Mock disk usage
            ]
        })
        
        # Time series data
        time_df = detections[['timestamp', 'FPS']].copy()
        time_df['timestamp'] = pd.to_datetime(time_df['timestamp'])
        time_df.rename(columns={'FPS': 'Detection Time'}, inplace=True)
        time_df['Temperature'] = float(system_stats['TEMP'].str.replace("'C", "").mean())  # Using average temp
        
        return (device_df, system_df, pi_df, time_df), None
        
    except Exception as e:
        print(e)
        return None, f"There was an error processing this file: {str(e)}"

@app.callback(
    Output('stored-data', 'data'),
    Output('output-data-upload', 'children'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def update_output(contents, filename):
    if contents is not None:
        data, error = parse_contents(contents, filename)
        if error:
            return None, dbc.Alert(error, color="danger")
        
        # Convert dataframes to dict for storage
        stored_data = {
            'device_df': data[0].to_dict('records'),
            'system_df': data[1].to_dict('records'),
            'pi_df': data[2].to_dict('records'),
            'time_df': data[3].to_dict('records')
        }
        
        return stored_data, dbc.Alert(f"Successfully loaded {filename}", color="success")
    return None, ""

@app.callback(
    [Output('device-distribution', 'figure'),
     Output('power-management', 'figure'),
     Output('power-management-table', 'data'),
     Output('system-performance', 'figure'),
     Output('raspberry-pi', 'figure'),
     Output('temperature-level', 'figure'),
     Output('object-detection-time', 'figure'),
     Output('kpi-cards', 'children')],
    [Input('interval-component', 'n_intervals'),
     Input('stored-data', 'data')]
)
def update_data(n_intervals, stored_data):
    if stored_data is None:
        # Return empty figures if no data uploaded
        empty_fig = go.Figure()
        empty_fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white'
        )
        empty_kpi = html.Div("Upload data to see KPIs")
        
        return (empty_fig, empty_fig, [], empty_fig, 
                empty_fig, empty_fig, empty_fig, empty_kpi)
    
    # Convert stored data back to dataframes
    device_df = pd.DataFrame(stored_data['device_df'])
    system_df = pd.DataFrame(stored_data['system_df'])
    pi_df = pd.DataFrame(stored_data['pi_df'])
    time_df = pd.DataFrame(stored_data['time_df'])
    time_df['timestamp'] = pd.to_datetime(time_df['timestamp'])

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
        x="timestamp", 
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
        x="timestamp", 
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
        temp_fig, detection_fig, kpi_cards
    )

# =============================================
# Run the App
# =============================================

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8050)
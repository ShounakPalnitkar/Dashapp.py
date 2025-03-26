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
        if 'csv' in filename.lower():
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename.lower():
            df = pd.read_excel(io.BytesIO(decoded))
        else:
            return None, "Unsupported file format. Please upload CSV or Excel."
        
        # Validate required columns
        required_cols = ['event_type', 'CPU', 'MEM', 'TEMP', 'FPS']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            return None, f"Missing required columns: {', '.join(missing_cols)}"
        
        # Process system stats
        system_stats = df[df['event_type'] == 'system_stats'].copy()
        if len(system_stats) == 0:
            return None, "No system stats data found"
        
        # Clean temperature data
        system_stats['TEMP'] = system_stats['TEMP'].str.replace("'C", "").astype(float)
        
        # Create device data
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
                system_stats['TEMP'].mean(),
                55,  # Mock GPU temp
                system_stats['MEM'].mean(),
                30   # Mock disk usage
            ]
        })
        
        # Time series data
        detections = df[df['event_type'] == 'detection']
        if len(detections) == 0:
            time_df = pd.DataFrame({
                'timestamp': [datetime.now() - timedelta(minutes=i) for i in range(60)],
                'Detection Time': [0]*60,
                'Temperature': [system_stats['TEMP'].mean()]*60
            })
        else:
            time_df = detections[['timestamp', 'FPS']].copy()
            time_df.rename(columns={'FPS': 'Detection Time'}, inplace=True)
            time_df['Temperature'] = system_stats['TEMP'].mean()
        
        # Convert timestamp
        time_df['timestamp'] = pd.to_datetime(time_df['timestamp'])
        
        return (device_df, system_df, pi_df, time_df), None
        
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        return None, f"There was an error processing this file: {str(e)}"

@app.callback(
    Output('stored-data', 'data'),
    Output('output-data-upload', 'children'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def update_output(contents, filename):
    if contents is None:
        return None, ""
    
    data, error = parse_contents(contents, filename)
    if error:
        return None, dbc.Alert(error, color="danger", className="mt-2")
    
    try:
        stored_data = {
            'device_df': data[0].to_dict('records'),
            'system_df': data[1].to_dict('records'),
            'pi_df': data[2].to_dict('records'),
            'time_df': data[3].to_dict('records')
        }
        return stored_data, dbc.Alert(
            f"Successfully loaded {filename} with {len(data[3])} records",
            color="success",
            className="mt-2"
        )
    except Exception as e:
        print(f"Error storing data: {str(e)}")
        return None, dbc.Alert(
            f"Error storing uploaded data: {str(e)}",
            color="danger",
            className="mt-2"
        )

def create_empty_figure():
    fig = go.Figure()
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        xaxis={'visible': False},
        yaxis={'visible': False},
        annotations=[{
            'text': 'No data available',
            'xref': 'paper',
            'yref': 'paper',
            'showarrow': False,
            'font': {'size': 16}
        }]
    )
    return fig

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
    # Create empty components
    empty_fig = create_empty_figure()
    empty_kpi = html.Div("Upload data to see KPIs", className="text-center")
    
    if stored_data is None:
        return ([empty_fig]*6 + [[], empty_kpi])
    
    try:
        # Safely convert stored data
        device_df = pd.DataFrame(stored_data.get('device_df', []))
        system_df = pd.DataFrame(stored_data.get('system_df', []))
        pi_df = pd.DataFrame(stored_data.get('pi_df', []))
        time_df = pd.DataFrame(stored_data.get('time_df', []))
        
        # Ensure required columns exist
        if 'Device' not in device_df.columns:
            device_df['Device'] = ["Camera", "Processor", "Sensors", "WiFi Module"][:len(device_df)]
        if 'Power Usage' not in device_df.columns:
            device_df['Power Usage'] = [2.5, 3.8, 1.2, 1.5][:len(device_df)]
        
        if 'Category' not in system_df.columns:
            system_df['Category'] = ["CPU", "Memory", "Storage", "Network"][:len(system_df)]
        if 'Value' not in system_df.columns:
            system_df['Value'] = [45, 32, 78, 12][:len(system_df)]
        
        if 'Category' not in pi_df.columns:
            pi_df['Category'] = ["CPU Temp", "GPU Temp", "Memory Usage", "Disk Usage"][:len(pi_df)]
        if 'Value' not in pi_df.columns:
            pi_df['Value'] = [65, 55, 45, 30][:len(pi_df)]
        
        # Create figures with error handling
        def safe_create_figure(fig_func, *args, **kwargs):
            try:
                return fig_func(*args, **kwargs).update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white'
                )
            except Exception as e:
                print(f"Error creating figure: {str(e)}")
                return empty_fig
        
        # Device Distribution
        device_fig = safe_create_figure(
            px.bar,
            device_df,
            x="Device",
            y="Power Usage",
            color="Device",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        
        # Power Management
        power_fig = safe_create_figure(
            px.bar,
            system_df,
            x="Value",
            y="Category",
            orientation='h',
            color="Category",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        # System Performance
        system_performance_fig = safe_create_figure(
            lambda: go.Figure(go.Pie(
                labels=system_df['Category'],
                values=system_df['Value'],
                hole=0.4,
                marker_colors=px.colors.sequential.Plasma,
                textinfo='percent+label'
            ))
        )
        
        # Raspberry Pi Health
        raspberry_pi_fig = safe_create_figure(
            lambda: go.Figure(go.Pie(
                labels=pi_df['Category'],
                values=pi_df['Value'],
                hole=0.4,
                marker_colors=px.colors.sequential.Viridis,
                textinfo='percent+label'
            ))
        )
        
        # Temperature Levels
        temp_fig = safe_create_figure(
            px.line,
            time_df,
            x="timestamp",
            y="Temperature",
            color_discrete_sequence=['#00CC96']
        ) if 'timestamp' in time_df.columns and 'Temperature' in time_df.columns else empty_fig
        
        # Object Detection Time
        detection_fig = safe_create_figure(
            px.line,
            time_df,
            x="timestamp",
            y="Detection Time",
            color_discrete_sequence=['#EF553B']
        ) if 'timestamp' in time_df.columns and 'Detection Time' in time_df.columns else empty_fig
        
        # KPI Cards with safe value access
        def safe_get_value(df, category):
            try:
                return df.loc[df['Category'] == category, 'Value'].values[0]
            except:
                return 0
        
        cpu_value = safe_get_value(system_df, 'CPU')
        mem_value = safe_get_value(system_df, 'Memory')
        
        try:
            power_sum = device_df['Power Usage'].sum()
        except:
            power_sum = 0
            
        detections_count = len(time_df) if not time_df.empty else 0
        
        kpi_cards = dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H4("CPU Load", className="card-title"),
                    html.H2(f"{cpu_value:.1f}%", className="card-text")
                ])
            ], color="primary", inverse=True), md=3, sm=6, xs=6, className="mb-3"),
            
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H4("RAM Usage", className="card-title"),
                    html.H2(f"{mem_value:.1f}%", className="card-text")
                ])
            ], color="success", inverse=True), md=3, sm=6, xs=6, className="mb-3"),
            
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H4("Power Usage", className="card-title"),
                    html.H2(f"{power_sum:.1f}W", className="card-text")
                ])
            ], color="warning", inverse=True), md=3, sm=6, xs=6, className="mb-3"),
            
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H4("Detections", className="card-title"),
                    html.H2(f"{detections_count}", className="card-text")
                ])
            ], color="danger", inverse=True), md=3, sm=6, xs=6, className="mb-3")
        ])
        
        return (
            device_fig,
            power_fig,
            device_df.to_dict('records'),
            system_performance_fig,
            raspberry_pi_fig,
            temp_fig,
            detection_fig,
            kpi_cards
        )
        
    except Exception as e:
        print(f"Error in update_data: {str(e)}")
        return ([empty_fig]*6 + [[], html.Div(f"Error: {str(e)}", className="text-center")])

# =============================================
# Run the App
# =============================================

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8050)
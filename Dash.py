import dash
from dash import dcc, html, Input, Output, dash_table, callback
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import requests
import dash_bootstrap_components as dbc

# Initialize the Dash app with Bootstrap
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

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
    
    # Second row: Power Management
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id='power-management', config=GRAPH_CONFIG)
                ])
            ], style=CARD_STYLE)
        ], md=8, xs=12),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dash_table.DataTable(
                        id='power-management-table',
                        columns=[{'name': 'Device', 'id': 'Device'}, 
                                {'name': 'Power Usage', 'id': 'Power Usage'}],
                        data=[],
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
                        },
                        style_data={
                            'border': 'none'
                        }
                    )
                ])
            ], style=CARD_STYLE)
        ], md=4, xs=12)
    ], className="mb-4"),
    
    # Third row: System Performance and Raspberry Pi
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id='system-performance', config=GRAPH_CONFIG)
                ])
            ], style=CARD_STYLE)
        ], md=6, xs=12),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id='raspberry-pi', config=GRAPH_CONFIG)
                ])
            ], style=CARD_STYLE)
        ], md=6, xs=12)
    ], className="mb-4"),
    
    # Fourth row: Temperature and Detection Time
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id='temperature-level', config=GRAPH_CONFIG)
                ])
            ], style=CARD_STYLE)
        ], md=6, xs=12),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id='object-detection-time', config=GRAPH_CONFIG)
                ])
            ], style=CARD_STYLE)
        ], md=6, xs=12)
    ], className="mb-4"),
    
    # Action Buttons
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
    
    # Download Button
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

# Callback to update data every 1 second
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
    device_df, system_df, pi_df, time_df = fetch_data()

    # Handle empty DataFrames
    if device_df.empty or system_df.empty or pi_df.empty or time_df.empty:
        print("Warning: One or more DataFrames are empty. Using placeholder data.")
        empty_fig = px.scatter(title="No Data Available")
        empty_fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            title={'x': 0.5, 'xanchor': 'center'}
        )
        
        return (
            empty_fig, empty_fig, [],
            empty_fig, empty_fig, empty_fig, empty_fig,
            dbc.Alert("No data available for KPIs", color="warning")
        )

    # Device Distribution
    device_fig = px.bar(
        device_df, 
        x="Device", 
        y="Power Usage", 
        title="Device Distribution",
        color="Device"
    )
    device_fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        title={'x': 0.5, 'xanchor': 'center'}
    )

    # Power Management
    power_fig = px.bar(
        system_df, 
        x="Value", 
        y="Category", 
        orientation='h', 
        title="Power Management",
        color="Category"
    )
    power_fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        title={'x': 0.5, 'xanchor': 'center'}
    )

    # Raspberry Pi performance
    raspberry_pi_fig = go.Figure(go.Pie(
        labels=pi_df['Category'], 
        values=pi_df['Value'], 
        hole=0.3,
        marker_colors=px.colors.sequential.Viridis
    ))
    raspberry_pi_fig.update_layout(
        title={'text': "Raspberry Pi Performance", 'x': 0.5, 'xanchor': 'center'},
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white'
    )

    # System Performance
    system_performance_fig = go.Figure(go.Pie(
        labels=system_df['Category'], 
        values=system_df['Value'],
        hole=0.3,
        marker_colors=px.colors.sequential.Plasma
    ))
    system_performance_fig.update_layout(
        title={'text': "System Performance", 'x': 0.5, 'xanchor': 'center'},
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white'
    )

    # Temperature Levels
    temp_fig = px.line(
        time_df, 
        x="Time", 
        y="Detection Time", 
        title="Temperature Levels",
        color_discrete_sequence=['#00CC96']
    )
    temp_fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        title={'x': 0.5, 'xanchor': 'center'}
    )

    # Object Detection Time
    detection_fig = px.line(
        time_df, 
        x="Time", 
        y="Detection Time", 
        title="Object Detection Time",
        color_discrete_sequence=['#EF553B']
    )
    detection_fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        title={'x': 0.5, 'xanchor': 'center'}
    )

    # KPI Cards
    kpi_cards = dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("CPU Load", className="card-title"),
                    html.H2(f"{system_df['Value'].mean():.1f}%", className="card-text")
                ])
            ], color="primary", inverse=True)
        ], md=3, sm=6, xs=6, className="mb-3"),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("RAM Usage", className="card-title"),
                    html.H2(f"{system_df['Value'].mean():.1f}%", className="card-text")
                ])
            ], color="success", inverse=True)
        ], md=3, sm=6, xs=6, className="mb-3"),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Power Usage", className="card-title"),
                    html.H2(f"{device_df['Power Usage'].sum():.1f}W", className="card-text")
                ])
            ], color="warning", inverse=True)
        ], md=3, sm=6, xs=6, className="mb-3"),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Detections", className="card-title"),
                    html.H2(f"{len(time_df)}", className="card-text")
                ])
            ], color="danger", inverse=True)
        ], md=3, sm=6, xs=6, className="mb-3")
    ])

    return (
        device_fig, power_fig, device_df.to_dict('records'),
        system_performance_fig, raspberry_pi_fig,
        temp_fig, detection_fig, kpi_cards
    )

# Running the server
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8050)